"""Tests for skills/diagram/scripts/check_drawio.py. No network, no draw.io install."""

import base64
import importlib.util
import urllib.parse
import zlib
from pathlib import Path
from xml.sax.saxutils import quoteattr

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "diagram" / "scripts" / "check_drawio.py"
spec = importlib.util.spec_from_file_location("check_drawio", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def cells(body: str) -> str:
    return f'<mxCell id="0"/><mxCell id="1" parent="0"/>{body}'


def page(body: str, name: str = "Page 1") -> str:
    return (f'<diagram id="p1" name="{name}"><mxGraphModel><root>{cells(body)}</root>'
            f"</mxGraphModel></diagram>")


def mxfile(*pages: str) -> str:
    return f'<mxfile host="test">{"".join(pages)}</mxfile>'


def vertex(cid: str, x: int, y: int, w: int = 120, h: int = 60, parent: str = "1") -> str:
    return (f'<mxCell id="{cid}" value="{cid}" style="rounded=1;" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge(cid: str, src: str, tgt: str) -> str:
    return (f'<mxCell id="{cid}" style="endArrow=classic;" edge="1" parent="1" '
            f'source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry"/></mxCell>')


def write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def run(path: Path, capsys) -> tuple[int, str]:
    code = check.main([str(path)])
    return code, capsys.readouterr().out


def test_valid_diagram_passes(tmp_path, capsys):
    body = vertex("web", 0, 0) + vertex("db", 300, 0) + edge("e1", "web", "db")
    code, out = run(write(tmp_path, "ok.drawio", mxfile(page(body))), capsys)
    assert code == 0
    assert "2 vertices, 1 edges" in out


def test_dangling_edge_target_is_reported(tmp_path, capsys):
    body = vertex("web", 0, 0) + edge("e1", "web", "missing")
    code, out = run(write(tmp_path, "bad.drawio", mxfile(page(body))), capsys)
    assert code == 1
    assert "edge 'e1' target 'missing' does not exist" in out


def test_edge_without_target_is_reported(tmp_path, capsys):
    body = vertex("web", 0, 0) + ('<mxCell id="e2" edge="1" parent="1" source="web">'
                                  '<mxGeometry relative="1" as="geometry"/></mxCell>')
    code, out = run(write(tmp_path, "floating.drawio", mxfile(page(body))), capsys)
    assert code == 1
    assert "edge 'e2' has no target" in out


def test_overlapping_vertices_are_reported(tmp_path, capsys):
    body = vertex("a", 0, 0, 120, 60) + vertex("b", 60, 30, 120, 60)
    code, out = run(write(tmp_path, "overlap.drawio", mxfile(page(body))), capsys)
    assert code == 1
    assert "vertices 'a' and 'b' overlap" in out


def test_touching_vertices_are_not_overlaps(tmp_path, capsys):
    body = vertex("a", 0, 0, 120, 60) + vertex("b", 120, 0, 120, 60)
    code, _ = run(write(tmp_path, "touch.drawio", mxfile(page(body))), capsys)
    assert code == 0


def test_child_inside_container_is_not_an_overlap(tmp_path, capsys):
    body = (vertex("zone", 0, 0, 400, 300)
            + vertex("api", 20, 40, 120, 60, parent="zone")
            + vertex("worker", 200, 40, 120, 60, parent="zone"))
    code, out = run(write(tmp_path, "zone.drawio", mxfile(page(body))), capsys)
    assert code == 0, out


def test_child_overlapping_a_sibling_outside_its_container_is_reported(tmp_path, capsys):
    body = vertex("zone", 0, 0, 400, 300) + vertex("outside", 350, 250, 120, 60)
    code, out = run(write(tmp_path, "zone2.drawio", mxfile(page(body))), capsys)
    assert code == 1
    assert "'zone' and 'outside' overlap" in out


def test_duplicate_id_and_missing_geometry(tmp_path, capsys):
    body = vertex("a", 0, 0) + vertex("a", 300, 0) + (
        '<mxCell id="nogeo" value="x" vertex="1" parent="1"/>')
    code, out = run(write(tmp_path, "dup.drawio", mxfile(page(body))), capsys)
    assert code == 1
    assert "duplicate cell id 'a'" in out
    assert "vertex 'nogeo' has no mxGeometry" in out


def test_malformed_xml_is_exit_2(tmp_path, capsys):
    code, out = run(write(tmp_path, "broken.drawio", "<mxfile><diagram>"), capsys)
    assert code == 2
    assert "cannot read" in out


def test_wrong_root_element_is_exit_2(tmp_path, capsys):
    code, out = run(write(tmp_path, "root.drawio", "<html/>"), capsys)
    assert code == 2
    assert "expected <mxfile>" in out


def test_drawio_svg_is_validated_through_its_content_attribute(tmp_path, capsys):
    inner = mxfile(page(vertex("web", 0, 0) + edge("e1", "web", "nowhere")))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="60" '
           f'content={quoteattr(inner)}><rect width="120" height="60"/></svg>')
    code, out = run(write(tmp_path, "arch.drawio.svg", svg), capsys)
    assert code == 1
    assert "target 'nowhere' does not exist" in out


def test_clean_drawio_svg_passes(tmp_path, capsys):
    inner = mxfile(page(vertex("web", 0, 0) + vertex("db", 300, 0) + edge("e1", "web", "db")))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" content={quoteattr(inner)}></svg>'
    code, _ = run(write(tmp_path, "clean.drawio.svg", svg), capsys)
    assert code == 0


def test_svg_without_content_attribute_is_exit_2(tmp_path, capsys):
    code, out = run(write(tmp_path, "plain.drawio.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>'), capsys)
    assert code == 2
    assert "no draw.io `content` attribute" in out


def test_compressed_page_is_decoded_and_checked(tmp_path, capsys):
    inner = f"<mxGraphModel><root>{cells(vertex('web', 0, 0) + edge('e1', 'web', 'gone'))}</root></mxGraphModel>"
    packed = zlib.compress(urllib.parse.quote(inner).encode("utf-8"))[2:-4]  # raw deflate
    encoded = base64.b64encode(packed).decode("ascii")
    xml = f'<mxfile><diagram id="c" name="Packed">{encoded}</diagram></mxfile>'
    code, out = run(write(tmp_path, "packed.drawio", xml), capsys)
    assert code == 1
    assert "'gone' does not exist" in out


def test_multiple_pages_are_each_checked(tmp_path, capsys):
    good = page(vertex("a", 0, 0), name="Overview")
    bad = page(vertex("b", 0, 0) + edge("e", "b", "x"), name="Detail")
    code, out = run(write(tmp_path, "pages.drawio", mxfile(good, bad)), capsys)
    assert code == 1
    assert "page 'Detail': edge 'e' target 'x'" in out


def test_cli_returns_worst_status(tmp_path, capsys):
    ok = write(tmp_path, "ok.drawio", mxfile(page(vertex("a", 0, 0))))
    broken = write(tmp_path, "broken.drawio", "<nope")
    assert check.main([str(ok), str(broken)]) == 2
    capsys.readouterr()


def test_no_arguments_prints_usage(capsys):
    assert check.main([]) == 2
    assert "Usage" in capsys.readouterr().out
