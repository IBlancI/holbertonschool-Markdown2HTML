#!/usr/bin/python3
"""
Script pour convertir des fichiers Markdown en HTML.
Supporte: Headers, Listes (non-ordonnées et ordonnées),
Gras, Emphase, et les extensions [[MD5]] et ((No-C)).
"""
import sys
import os
import re
import hashlib


def md5_hash(text):
    """Calcule le hash MD5 (en minuscules) d'une chaîne de texte."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def remove_c_chars(text):
    """Supprime tous les caractères 'c' (insensible à la casse) d'une chaîne."""
    return re.sub(r'[cC]', '', text)


def parse_inline_formatting(line):
    """
    Parse et convertit le formatage en ligne:
    [[text]] -> MD5, ((text)) -> suppression de 'c',
    **text** -> <b>text</b>, __text__ -> <em>text</em>.
    """
    # 1. Traiter [[text]] - conversion MD5
    line = re.sub(r'\[\[([^\]]+)\]\]', lambda m: md5_hash(m.group(1)), line)

    # 2. Traiter ((text)) - suppression des 'c'
    line = re.sub(r'\(\(([^)]+)\)\)', lambda m: remove_c_chars(m.group(1)), line)

    # 3. Traiter **text** - gras (conversion correcte)
    line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)

    # 4. Traiter __text__ - emphase (conversion correcte)
    line = re.sub(r'__([^_]+)__', r'<em>\1</em>', line)

    return line


def process_list_block(lines, start_index, list_char, list_tag):
    """Traite un bloc de liste (ul ou ol) et retourne le contenu HTML et le nouvel index."""
    list_content = [f'<{list_tag}>']
    i = start_index

    while i < len(lines):
        line = lines[i].rstrip('\n')
        prefix = f'{list_char} '

        if line.startswith(prefix):
            item_text = line[len(prefix):].strip()
            item_text = parse_inline_formatting(item_text)
            list_content.append(f'<li>{item_text}</li>')
            i += 1
        # Une ligne vide termine la liste
        elif not line.strip():
            # Avancer au-delà de la ligne vide
            i += 1
            break
        # Tout autre bloc de contenu termine la liste
        else:
            break

    list_content.append(f'</{list_tag}>')
    return list_content, i


def convert_markdown_to_html(markdown_file, html_file):
    """Convertit un fichier Markdown en HTML, ligne par ligne."""

    with open(markdown_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html_content = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip('\n')

        # 1. Ignorer les lignes vides
        if not line.strip():
            i += 1
            continue

        # 2. Headers (#, ##, etc.)
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))

            # Le header doit avoir un espace après les '#'
            if 1 <= level <= 6 and line[level:level + 1] == ' ':
                header_text = line[level + 1:].strip()
                header_text = parse_inline_formatting(header_text)
                html_content.append(f'<h{level}>{header_text}</h{level}>')
                i += 1
                continue
        
        # 3. Listes non-ordonnées (-)
        if line.startswith('- '):
            list_html, next_i = process_list_block(lines, i, '-', 'ul')
            html_content.extend(list_html)
            i = next_i
            continue

        # 4. Listes ordonnées (*) (selon les exigences du test)
        if line.startswith('* '):
            list_html, next_i = process_list_block(lines, i, '*', 'ol')
            html_content.extend(list_html)
            i = next_i
            continue

        # 5. Paragraphes
        if line.strip():
            paragraph_lines = []
            
            # Collecter toutes les lignes consécutives qui ne sont pas des headers ou des listes
            while i < len(lines):
                current_line = lines[i].rstrip('\n')
                
                # Arrêter si ligne vide ou début d'un autre élément
                if not current_line.strip() or current_line.startswith('#') or \
                   current_line.startswith('- ') or current_line.startswith('* '):
                    break
                
                paragraph_lines.append(current_line)
                i += 1
            
            # Joindre les lignes et appliquer le formatage en ligne
            paragraph_text = ' '.join(paragraph_lines)
            paragraph_text = parse_inline_formatting(paragraph_text)
            
            html_content.append(f'<p>{paragraph_text}</p>')
            continue # Avancer au début du bloc suivant

    # Écrire le contenu HTML
    with open(html_file, 'w', encoding='utf-8') as html:
        html.write('\n'.join(html_content) + '\n')


def main():
    """Fonction principale pour gérer la conversion Markdown vers HTML."""
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    markdown_file = sys.argv[1]
    html_file = sys.argv[2]

    if not os.path.exists(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)

    try:
        convert_markdown_to_html(markdown_file, html_file)
    except Exception as e:
        # En cas d'erreur de lecture/écriture (peu probable ici)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()