import * as THREE from 'three';

/**
 * ParticleMorph — particle cloud Three.js hội tụ thành ảnh theo tiến độ cuộn.
 *
 * Cơ chế (viết gốc, không copy demo nào):
 * 1. Vẽ ảnh nguồn lên canvas ẩn (offscreen), đọc getImageData().
 * 2. Duyệt pixel theo bước nhảy (stride) — KHÔNG lấy hết mọi pixel, quá nặng —
 *    giữ lại pixel đủ sáng/không trong suốt làm toạ độ đích (target) + màu.
 * 3. Mỗi target -> 1 particle trong THREE.Points (BufferGeometry). Vị trí khởi tạo
 *    ngẫu nhiên trong không gian 3D (start), vị trí đích là toạ độ pixel đã sample.
 * 4. Mỗi frame: progress mượt dần tới targetProgress (đọc từ scroll, rAF-throttle),
 *    position[i] = lerp(start[i], target[i], progress) rồi set needsUpdate = true.
 */
export class ParticleMorph {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {object} [opts]
   * @param {string|null} [opts.imageUrl] - ảnh nguồn để sample; null = demo tự vẽ chữ mẫu.
   * @param {number} [opts.particleCount] - số particle mục tiêu (xem Rules về ngưỡng hiệu năng).
   * @param {number} [opts.particleSize] - kích thước điểm (PointsMaterial.size).
   * @param {number} [opts.sampleResolution] - độ phân giải canvas ẩn dùng để sample (px).
   * @param {number} [opts.alphaThreshold] - bỏ qua pixel có alpha dưới ngưỡng này (0-255).
   * @param {HTMLElement} [opts.scrollRoot] - phần tử quyết định chiều cao vùng cuộn (mặc định document).
   */
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.imageUrl = opts.imageUrl ?? null;
    this.particleCount = opts.particleCount ?? 6000;
    this.particleSize = opts.particleSize ?? 2.2;
    this.sampleResolution = opts.sampleResolution ?? 220;
    this.alphaThreshold = opts.alphaThreshold ?? 32;
    this.scrollRoot = opts.scrollRoot ?? document.documentElement;
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    this.progress = 0;
    this.targetProgress = 0;
    this._destroyed = false;
    this._rafId = null;

    this._onScroll = this._onScroll.bind(this);
    this._onResize = this._onResize.bind(this);
    this._tick = this._tick.bind(this);
  }

  async init() {
    const samples = await this._buildSamples();
    this._buildScene(samples);
    this._bindEvents();
    this._tick();
    return this;
  }

  // --- Bước 1+2: sample ảnh thành danh sách {x, y, r, g, b} ---
  async _buildSamples() {
    const size = this.sampleResolution;
    const off = document.createElement('canvas');
    off.width = size;
    off.height = size;
    const ctx = off.getContext('2d', { willReadFrequently: true });

    if (this.imageUrl) {
      const img = await this._loadImage(this.imageUrl);
      // cover-fit ảnh vào canvas vuông
      const scale = Math.max(size / img.width, size / img.height);
      const w = img.width * scale;
      const h = img.height * scale;
      ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h);
    } else {
      // Demo tự chủ, không phụ thuộc mạng: vẽ chữ mẫu để sample.
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = '#fff';
      ctx.font = `bold ${Math.floor(size * 0.22)}px system-ui, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('OVERSTACK', size / 2, size / 2);
    }

    const { data } = ctx.getImageData(0, 0, size, size);
    const points = [];
    // Bước nhảy tính từ particleCount mong muốn so với tổng pixel — sample thưa, không lấy hết.
    const stride = Math.max(1, Math.round(Math.sqrt((size * size) / this.particleCount)));

    for (let y = 0; y < size; y += stride) {
      for (let x = 0; x < size; x += stride) {
        const i = (y * size + x) * 4;
        const alpha = data[i + 3];
        const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
        if (alpha < this.alphaThreshold || brightness < 24) continue;
        points.push({
          x: (x / size - 0.5) * 180,
          y: -(y / size - 0.5) * 180,
          r: data[i] / 255,
          g: data[i + 1] / 255,
          b: data[i + 2] / 255,
        });
      }
    }
    return points;
  }

  _loadImage(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    });
  }

  // --- Bước 3: dựng THREE.Points từ samples ---
  _buildScene(samples) {
    const count = samples.length;
    const starts = new Float32Array(count * 3);
    const targets = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const spread = 220; // bán kính vùng particle "nổ tung" trước khi hội tụ

    for (let i = 0; i < count; i++) {
      const p = samples[i];
      const b = i * 3;
      starts[b] = (Math.random() - 0.5) * spread;
      starts[b + 1] = (Math.random() - 0.5) * spread;
      starts[b + 2] = (Math.random() - 0.5) * spread - 80;

      targets[b] = p.x;
      targets[b + 1] = p.y;
      targets[b + 2] = (Math.random() - 0.5) * 12; // độ dày nhẹ, tránh phẳng lì

      colors[b] = p.r;
      colors[b + 1] = p.g;
      colors[b + 2] = p.b;
    }

    this._starts = starts;
    this._targets = targets;

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(starts.slice(), 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: this.particleSize,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
    });

    this.geometry = geometry;
    this.material = material;
    this.points = new THREE.Points(geometry, material);

    this.scene = new THREE.Scene();
    this.scene.add(this.points);

    this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 2000);
    this.camera.position.z = 260;

    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this._resize();
  }

  _bindEvents() {
    window.addEventListener('scroll', this._onScroll, { passive: true });
    window.addEventListener('resize', this._onResize);
  }

  // Scroll listener rAF-throttle thuần — không GSAP/ScrollTrigger (xem SKILL.md).
  _onScroll() {
    if (this._scrollScheduled) return;
    this._scrollScheduled = true;
    requestAnimationFrame(() => {
      this._scrollScheduled = false;
      const max = this.scrollRoot.scrollHeight - window.innerHeight;
      this.targetProgress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    });
  }

  _onResize() {
    this._resize();
  }

  _resize() {
    const w = this.canvas.clientWidth || window.innerWidth;
    const h = this.canvas.clientHeight || window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h, false);
  }

  // --- Bước 4: lerp position mỗi frame theo progress đã làm mượt ---
  _tick() {
    if (this._destroyed) return;

    this.progress = this.reducedMotion
      ? this.targetProgress
      : this.progress + (this.targetProgress - this.progress) * 0.08;

    const position = this.geometry.attributes.position.array;
    for (let i = 0; i < position.length; i++) {
      position[i] = this._starts[i] + (this._targets[i] - this._starts[i]) * this.progress;
    }
    this.geometry.attributes.position.needsUpdate = true;

    this.points.rotation.y = this.progress * 0.15; // xoay nhẹ, gợi chiều sâu 3D

    this.renderer.render(this.scene, this.camera);
    this._rafId = requestAnimationFrame(this._tick);
  }

  // Cleanup đúng: huỷ rAF, gỡ listener, dispose geometry/material/renderer.
  destroy() {
    this._destroyed = true;
    if (this._rafId) cancelAnimationFrame(this._rafId);
    window.removeEventListener('scroll', this._onScroll);
    window.removeEventListener('resize', this._onResize);
    this.geometry?.dispose();
    this.material?.dispose();
    this.renderer?.dispose();
  }
}

// --- Bootstrap demo ---
const canvas = document.getElementById('morph-canvas');
const morph = new ParticleMorph(canvas, { particleCount: 6000 });
morph.init();
window.__particleMorph = morph; // tiện destroy() từ console khi test tay
