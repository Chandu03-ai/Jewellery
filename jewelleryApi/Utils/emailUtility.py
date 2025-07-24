def loadHtmlTemplate(templatePath: str, replacements: dict) -> str:
    try:
        with open(templatePath, "r", encoding="utf-8") as file:
            content = file.read()
            for key, value in replacements.items():
                content = content.replace(f"{{{{ {key} }}}}", str(value))  # Jinja-style
                content = content.replace(f"{{{{{key}}}}}", str(value))  # no-space style
            return content
    except Exception as e:
        raise RuntimeError(f"Error reading HTML template: {e}")
