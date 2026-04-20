#!/usr/bin/env python3
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = [
    (ROOT / "baselines/google.png", "Эталон полной страницы (viewport)"),
    (ROOT / "diffs/google_search_form.png", "Скриншот элемента — поле поиска"),
]


def main() -> None:
    parts: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="ru">',
        "<head>",
        '<meta charset="utf-8"/>',
        "<title>Отчёт — визуальное тестирование Google</title>",
        "<style>",
        "body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }",
        "h1 { font-size: 1.5rem; }",
        "h2 { font-size: 1.15rem; margin-top: 2rem; }",
        "figure { margin: 1rem 0; }",
        "img { max-width: 100%; height: auto; border: 1px solid #ddd; }",
        "figcaption { color: #444; font-size: 0.9rem; margin-top: 0.5rem; }",
        "code { background: #f4f4f4; padding: 0.1em 0.35em; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Отчёт по автоматизированному визуальному тестированию</h1>",
        "<p><strong>Объект:</strong> главная страница Google.</p>",
        "<p>Скриншоты ниже <strong>встроены в этот файл</strong> (не зависят от путей на диске).</p>",
        "<h2>Скриншоты</h2>",
    ]
    for path, caption in IMAGES:
        if not path.is_file():
            parts.append(f'<p style="color:#b00">Нет файла: <code>{path.name}</code> — сначала запустите <code>pytest</code>.</p>')
            continue
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        parts.append("<figure>")
        parts.append(
            f'<img src="data:image/png;base64,{b64}" alt="{caption}"/>'
        )
        parts.append(f"<figcaption>{caption}<br/><code>{path.relative_to(ROOT)}</code></figcaption>")
        parts.append("</figure>")
    parts.extend(
        [
            "<h2>Файлы проекта</h2>",
            "<ul>",
            "<li><code>baselines/google.png</code> — эталон для сравнения phash</li>",
            "<li><code>diffs/google_search_form.png</code> — элемент интерфейса</li>",
            "<li><code>allure-report/index.html</code> — отчёт Allure после <code>allure generate</code></li>",
            "</ul>",
            "</body>",
            "</html>",
        ]
    )
    out = ROOT / "REPORT.html"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"OK: {out}")


if __name__ == "__main__":
    main()
