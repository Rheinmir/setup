// infinite-webgl-grid — lưới ảnh WebGL cuộn/kéo vô hạn qua coordinate-wrapping.
// Kỹ thuật GỐC viết lại từ mô tả chung (THREE.js + modulo offset), KHÔNG copy
// code của tác giả CodePen cụ thể nào. Xem SKILL.md mục Origin.
import * as THREE from 'three';

/**
 * InfiniteGrid — N×N tile PlaneGeometry cố định, không bao giờ tạo/huỷ mesh
 * lúc chạy. Kéo/cuộn chỉ dịch một offset ảo; vị trí hiển thị của mỗi mesh
 * được tính lại bằng modulo (wrap) quanh offset đó, nên lưới trông vô hạn
 * dù chỉ có gridSize*gridSize mesh thật tồn tại.
 */
export class InfiniteGrid {
  constructor(container, options = {}) {
    this.container = container;

    // gridSize gồm vùng hiển thị + 1 vòng đệm mỗi bên để tile "nhảy cóc"
    // sang phía đối diện trước khi rời khung nhìn (không bị pop-in thấy được).
    // Xem Rules trong SKILL.md về ngưỡng an toàn cho mobile GPU.
    this.gridSize = options.gridSize ?? 7;
    this.tileSize = options.tileSize ?? 200;
    this.gap = options.gap ?? 16;
    this.poolSize = options.poolSize ?? 12;
    this.wheelSpeed = options.wheelSpeed ?? 1;
    this.damping = options.damping ?? 0.92; // inertia: velocity *= damping mỗi frame

    this.pitch = this.tileSize + this.gap;
    this.fullSpan = this.gridSize * this.pitch;
    this.half = this.fullSpan / 2;

    this.offset = { x: 0, y: 0 };
    this.velocity = { x: 0, y: 0 };
    this.dragging = false;
    this._lastPointer = { x: 0, y: 0 };
    this._rafId = null;
    this._destroyed = false;

    this.meshes = [];
    this.pool = [];

    this._onPointerDown = this._onPointerDown.bind(this);
    this._onPointerMove = this._onPointerMove.bind(this);
    this._onPointerUp = this._onPointerUp.bind(this);
    this._onWheel = this._onWheel.bind(this);
    this._onResize = this._onResize.bind(this);
    this._tick = this._tick.bind(this);

    this._init();
  }

  async _init() {
    const { clientWidth: w, clientHeight: h } = this.container;

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.setSize(w, h);
    this.container.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x101014);

    // Ortho: 1 world-unit ~= 1 px màn hình, lưới không méo phối cảnh — phù
    // hợp cho "tường ảnh" phẳng thay vì cảnh 3D có chiều sâu.
    this.camera = new THREE.OrthographicCamera(-w / 2, w / 2, h / 2, -h / 2, 0.1, 10);
    this.camera.position.z = 5;

    this.geometry = new THREE.PlaneGeometry(this.tileSize, this.tileSize);

    this.pool = await this._buildTexturePool(this.poolSize);
    if (this._destroyed) return; // huỷ trong lúc đang load (unmount nhanh)

    this._buildTiles();
    this._bindEvents();
    this._onResize();
    this._tick();
  }

  /** Sinh poolSize texture placeholder (canvas vẽ số) qua THREE.TextureLoader,
   *  không phụ thuộc mạng/ảnh ngoài — chỉ dùng data URL sinh cục bộ. */
  _buildTexturePool(count) {
    const loader = new THREE.TextureLoader();
    const jobs = [];
    for (let n = 0; n < count; n++) {
      const dataUrl = this._drawPlaceholder(n);
      jobs.push(
        new Promise((resolve, reject) => {
          loader.load(dataUrl, (tex) => {
            tex.colorSpace = THREE.SRGBColorSpace;
            resolve(tex);
          }, undefined, reject);
        })
      );
    }
    return Promise.all(jobs);
  }

  _drawPlaceholder(n) {
    const size = 256;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    const hue = (n * 137.5) % 360; // golden-angle spread, phân biệt tile bằng mắt
    ctx.fillStyle = `hsl(${hue}, 45%, 32%)`;
    ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 4;
    ctx.strokeRect(2, 2, size - 4, size - 4);
    ctx.fillStyle = '#f4f4f5';
    ctx.font = 'bold 96px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(n), size / 2, size / 2);
    return canvas.toDataURL('image/png');
  }

  _buildTiles() {
    const n = this.gridSize;
    const offsetIndex = (n - 1) / 2;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const localX = (i - offsetIndex) * this.pitch;
        const localY = (j - offsetIndex) * this.pitch;
        const material = new THREE.MeshBasicMaterial({ map: this.pool[0] });
        const mesh = new THREE.Mesh(this.geometry, material);
        mesh.userData = { localX, localY, poolIndex: 0 };
        this.scene.add(mesh);
        this.meshes.push(mesh);
      }
    }
    this._layoutTiles();
  }

  /** position.x = ((raw + half) % full + full) % full - half — kỹ thuật wrap
   *  chuẩn: gấp toạ độ vô hạn về dải hiển thị [-half, half). */
  _wrap(raw) {
    const full = this.fullSpan;
    const half = this.half;
    return (((raw + half) % full) + full) % full - half;
  }

  _layoutTiles() {
    for (const mesh of this.meshes) {
      const rawX = mesh.userData.localX - this.offset.x;
      const rawY = mesh.userData.localY - this.offset.y;
      const x = this._wrap(rawX);
      const y = this._wrap(rawY);
      mesh.position.set(x, y, 0);

      // Toạ độ "thật" trong không gian vô hạn (trước khi wrap) → chỉ số
      // tile ảo, dùng để chọn texture trong pool. Tile chỉ đổi texture khi
      // chỉ số ảo đổi (tức là lúc nó vừa nhảy cóc sang phía đối diện) —
      // đây là bước "tái sử dụng texture" thay vì tạo texture mới.
      const trueX = x + this.offset.x;
      const trueY = y + this.offset.y;
      const idxX = Math.round(trueX / this.pitch);
      const idxY = Math.round(trueY / this.pitch);
      const poolIndex = Math.abs((idxX * 73856093) ^ (idxY * 19349663)) % this.pool.length;
      if (poolIndex !== mesh.userData.poolIndex) {
        mesh.userData.poolIndex = poolIndex;
        mesh.material.map = this.pool[poolIndex];
        mesh.material.needsUpdate = true;
      }
    }
  }

  _bindEvents() {
    const el = this.renderer.domElement;
    el.addEventListener('pointerdown', this._onPointerDown);
    // move/wheel cần passive:false vì ta preventDefault để chặn cuộn/zoom
    // trang nền — trình duyệt hiện đại mặc định passive:true cho các event
    // này, preventDefault bị bỏ qua âm thầm nếu thiếu cờ này.
    window.addEventListener('pointermove', this._onPointerMove, { passive: false });
    window.addEventListener('pointerup', this._onPointerUp, { passive: false });
    window.addEventListener('pointercancel', this._onPointerUp, { passive: false });
    el.addEventListener('wheel', this._onWheel, { passive: false });
    window.addEventListener('resize', this._onResize);
  }

  _onPointerDown(e) {
    this.dragging = true;
    this.container.classList.add('dragging');
    this._lastPointer.x = e.clientX;
    this._lastPointer.y = e.clientY;
    this.velocity.x = 0;
    this.velocity.y = 0;
  }

  _onPointerMove(e) {
    if (!this.dragging) return;
    e.preventDefault();
    const dx = e.clientX - this._lastPointer.x;
    const dy = e.clientY - this._lastPointer.y;
    this._lastPointer.x = e.clientX;
    this._lastPointer.y = e.clientY;
    this.offset.x -= dx;
    this.offset.y += dy;
    this.velocity.x = -dx;
    this.velocity.y = dy;
  }

  _onPointerUp() {
    this.dragging = false;
    this.container.classList.remove('dragging');
    // velocity giữ nguyên → vòng _tick() sẽ lerp nó về 0 (inertia).
  }

  _onWheel(e) {
    e.preventDefault();
    const dx = e.deltaX * this.wheelSpeed;
    const dy = e.deltaY * this.wheelSpeed;
    this.offset.x += dx;
    this.offset.y -= dy;
    this.velocity.x += dx * 0.3;
    this.velocity.y -= dy * 0.3;
  }

  _onResize() {
    const { clientWidth: w, clientHeight: h } = this.container;
    this.camera.left = -w / 2;
    this.camera.right = w / 2;
    this.camera.top = h / 2;
    this.camera.bottom = -h / 2;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  _tick() {
    if (this._destroyed) return;
    this._rafId = requestAnimationFrame(this._tick);

    if (!this.dragging) {
      // inertia: lerp velocity về 0 dần bằng damping mũ, không phải vật lý
      // chính xác — đủ cho cảm giác "thả tay còn trôi nhẹ".
      const EPS = 0.02;
      if (Math.abs(this.velocity.x) > EPS || Math.abs(this.velocity.y) > EPS) {
        this.offset.x += this.velocity.x;
        this.offset.y += this.velocity.y;
        this.velocity.x *= this.damping;
        this.velocity.y *= this.damping;
      } else {
        this.velocity.x = 0;
        this.velocity.y = 0;
      }
    }

    this._layoutTiles();
    this.renderer.render(this.scene, this.camera);
  }

  /** Dừng render, gỡ mọi listener, dispose toàn bộ tài nguyên GPU. */
  destroy() {
    this._destroyed = true;
    if (this._rafId) cancelAnimationFrame(this._rafId);

    const el = this.renderer?.domElement;
    if (el) {
      el.removeEventListener('pointerdown', this._onPointerDown);
      el.removeEventListener('wheel', this._onWheel);
    }
    window.removeEventListener('pointermove', this._onPointerMove);
    window.removeEventListener('pointerup', this._onPointerUp);
    window.removeEventListener('pointercancel', this._onPointerUp);
    window.removeEventListener('resize', this._onResize);

    for (const mesh of this.meshes) {
      mesh.material.dispose(); // material riêng mỗi mesh — texture (map) KHÔNG bị dispose ở đây
    }
    this.geometry?.dispose(); // geometry dùng chung 1 instance cho mọi mesh
    for (const tex of this.pool) tex.dispose(); // pool texture dispose riêng, một lần
    this.renderer?.dispose();
    if (el && el.parentNode) el.parentNode.removeChild(el);

    this.meshes = [];
    this.pool = [];
  }
}

// Auto-mount khi mở demo.html trực tiếp.
const root = document.getElementById('grid-root');
if (root) {
  const grid = new InfiniteGrid(root);
  window.addEventListener('beforeunload', () => grid.destroy());
}
