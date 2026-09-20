"""test_repo_role — nhãn repo là KHAI BÁO; suy theo hình dạng chỉ là phương án lùi có bằng chứng; repo `foreign` không bao giờ bị ghi."""
import importlib.util, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "harness/scripts/repo_role.py"


def rr(root, *args, home=None):
    env = dict(os.environ, OVERSTACK_HARNESS_HOME=str(home or Path(root) / "_gh"))
    return subprocess.run([sys.executable, str(SCRIPT), str(root), *args], capture_output=True, text=True, env=env)


def mk(tmp, name, files=()):
    d = tmp / name; d.mkdir()
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    for f in files:
        p = d / f; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("x")
    return d


def test_inference_carries_evidence_for_each_role(tmp_path):
    cases = {"framework": ["fdk/wiki/index.md"], "downstream": [".llmwiki/.harness-stamp"], "foreign": ["src/app.py"]}
    for role, files in cases.items():
        r = json.loads(rr(mk(tmp_path, role, files), "--json").stdout)
        assert (r["role"], r["source"]) == (role, "inferred") and r["evidence"], r
    d = mk(tmp_path, "mod"); (d / ".overstack.yaml").write_text("upstream_pin: {repo: Rheinmir/setup}\n")
    assert json.loads(rr(d, "--json").stdout)["role"] == "module"


def test_declared_label_beats_directory_shape(tmp_path):
    d = mk(tmp_path, "looks-like-framework", ["fdk/wiki/index.md"])
    (d / ".overstack.yaml").write_text("wiki_dir: docs/wiki\nrepo_role: downstream   # fork để thử\n")
    r = json.loads(rr(d, "--json").stdout)
    assert (r["role"], r["source"]) == ("downstream", "declared")
    (d / ".overstack.yaml").write_text("repo_role: vibes\n")
    assert rr(d).returncode != 0


def test_set_writes_yaml_but_foreign_never_touches_the_repo(tmp_path):
    d = mk(tmp_path, "proj"); (d / ".overstack.yaml").write_text("wiki_dir: .llmwiki/wiki\n")
    assert rr(d, "--set", "downstream").returncode == 0
    assert (d / ".overstack.yaml").read_text() == "wiki_dir: .llmwiki/wiki\nrepo_role: downstream\n"      # giữ khoá cũ, thêm đúng một dòng
    assert rr(d, "--set", "module").returncode == 0 and (d / ".overstack.yaml").read_text().count("repo_role:") == 1
    f = mk(tmp_path, "theirs", ["README.md"]); gh = tmp_path / "gh"
    subprocess.run(["git", "-C", str(f), "remote", "add", "origin", "git@github.com:Someone/Their-Repo.git"], check=True)
    before = sorted(p.name for p in f.iterdir())
    assert rr(f, "--set", "foreign", home=gh).returncode == 0
    assert sorted(p.name for p in f.iterdir()) == before                                                # repo người khác: KHÔNG thêm file nào
    assert json.loads((gh / "repo-roles.json").read_text()) == {"github.com/someone/their-repo": "foreign"}
    r = json.loads(rr(f, "--json", home=gh).stdout)
    assert (r["role"], r["source"]) == ("foreign", "machine")


def test_this_repo_and_plain_output(tmp_path):
    assert rr(ROOT).stdout.strip() == "framework"


def test_review_V1_V2_set_keeps_comments_and_remote_forms_share_one_key(tmp_path):
    d = mk(tmp_path, "keep"); y = d / ".overstack.yaml"
    y.write_text("repo_role: module\n\n# ghi chú quan trọng\nwiki_dir: x\n")
    assert rr(d, "--set", "downstream").returncode == 0
    assert y.read_text() == "repo_role: downstream\n\n# ghi chú quan trọng\nwiki_dir: x\n"     # \s* từng nuốt dòng trống + comment
    y.write_text("repo_role:\nframework\n")
    assert json.loads(rr(d, "--json").stdout)["source"] != "declared"                            # giá trị ở DÒNG DƯỚI không phải nhãn
    y.write_text('repo_role: "module"\n')
    assert json.loads(rr(d, "--json").stdout)["role"] == "module"                                # nhãn có nháy vẫn nhận
    spec = importlib.util.spec_from_file_location("repo_role", SCRIPT); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    keys = set()
    for url in ("git@github.com:A/B.git", "https://github.com/A/B", "ssh://git@github.com/A/B.git", "https://user@github.com/A/B.git", "https://github.com/A/B/"):
        r = mk(tmp_path, "r%d" % len(keys | {url}) + str(abs(hash(url)) % 9999)); subprocess.run(["git", "-C", str(r), "remote", "add", "origin", url], check=True)
        keys.add(m._remote(r))
    assert keys == {"github.com/a/b"}, keys
