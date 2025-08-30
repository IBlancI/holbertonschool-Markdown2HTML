#!/usr/bin/python3
"""
Script to convert Markdown to HTML.
"""
import sys
import os


def convert_markdown_to_html(content):
    """Convert markdown content to HTML"""
    html_lines = []
    current_list = []
    in_list = False
    
    for line in content.split('\n'):
        # Skip empty lines
        if not line.strip():
            if in_list:
                # Close the current list
                html_lines.append("<ul>")
                for item in current_list:
                    html_lines.append(f"<li>{item}</li>")
                html_lines.append("</ul>")
                current_list = []
                in_list = False
            continue
            
        # Handle unordered lists
        if line.strip().startswith('- '):
            in_list = True
            current_list.append(line.strip()[2:])
            continue
            
        # If we were in a list and now we're not
        if in_list and not line.strip().startswith('- '):
            html_lines.append("<ul>")
            for item in current_list:
                html_lines.append(f"<li>{item}</li>")
            html_lines.append("</ul>")
            current_list = []
            in_list = False
            
        # Handle headers
        if line.startswith('#'):
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
                    
            if 1 <= level <= 6:
                header_text = line[level:].strip()
                html_lines.append(f"<h{level}>{header_text}</h{level}>")
        else:
            if not in_list:
                html_lines.append(line)
    
    # If we end the file while still in a list
    if in_list:
        html_lines.append("<ul>")
        for item in current_list:
            html_lines.append(f"<li>{item}</li>")
        html_lines.append("</ul>")
    
    return '\n'.join(html_lines)


def main():
    """Main function to handle markdown to html conversion"""
    # Vérifier le nombre d'arguments
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    # Récupérer les noms de fichiers des arguments
    markdown_file = sys.argv[1]
    html_file = sys.argv[2]

    # Vérifier si le fichier markdown existe
    if not os.path.exists(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)

    try:
        # Lire le contenu du fichier markdown
        with open(markdown_file, 'r') as md:
            content = md.read()

        # Convertir le markdown en HTML
        html_content = convert_markdown_to_html(content)

        # Écrire le contenu HTML dans le fichier de sortie
        with open(html_file, 'w') as html:
            html.write(html_content)

    except Exception as e:
        sys.exit(1)

    # Si tout est OK, sortir avec succès
    sys.exit(0)


if __name__ == "__main__":
    main()