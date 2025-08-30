#!/usr/bin/env python3
"""
Script pour convertir des fichiers Markdown en HTML
"""

import sys
import os
import re
import hashlib


def md5_hash(text):
    """Convertit le texte en hash MD5 (minuscules)"""
    return hashlib.md5(text.encode()).hexdigest()


def remove_c_chars(text):
    """Supprime tous les caractères 'c' (insensible à la casse)"""
    return re.sub(r'[cC]', '', text)


def parse_inline_formatting(line):
    """Parse le formatage en ligne : gras, emphase, MD5, et suppression de 'c'"""
    # Traiter [[text]] - conversion MD5
    line = re.sub(r'\[\[([^\]]+)\]\]', lambda m: md5_hash(m.group(1)), line)
    
    # Traiter ((text)) - suppression des 'c'
    line = re.sub(r'\(\(([^)]+)\)\)', lambda m: remove_c_chars(m.group(1)), line)
    
    # Traiter **text** - gras
    line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
    
    # Traiter __text__ - emphase
    line = re.sub(r'__([^_]+)__', r'<em>\1</em>', line)
    
    return line


def convert_markdown_to_html(markdown_file, html_file):
    """Convertit un fichier Markdown en HTML"""
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    html_content = []
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        # Ignorer les lignes vides au début
        if not line.strip():
            i += 1
            continue
        
        # Headers (#, ##, ###, etc.)
        if line.startswith('#'):
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
            
            if level <= 6 and line[level:level+1] == ' ':
                header_text = line[level+1:].strip()
                header_text = parse_inline_formatting(header_text)
                html_content.append(f'<h{level}>{header_text}</h{level}>')
            
            i += 1
            continue
        
        # Listes non-ordonnées (-)
        if line.startswith('- '):
            html_content.append('<ul>')
            while i < len(lines) and lines[i].startswith('- '):
                item_text = lines[i][2:].strip()
                item_text = parse_inline_formatting(item_text)
                html_content.append(f'<li>{item_text}</li>')
                i += 1
            html_content.append('</ul>')
            continue
        
        # Listes ordonnées (*)
        if line.startswith('* '):
            html_content.append('<ol>')
            while i < len(lines) and lines[i].startswith('* '):
                item_text = lines[i][2:].strip()
                item_text = parse_inline_formatting(item_text)
                html_content.append(f'<li>{item_text}</li>')
                i += 1
            html_content.append('</ol>')
            continue
        
        # Paragraphes
        if line.strip():
            html_content.append('<p>')
            paragraph_lines = []
            
            # Collecter toutes les lignes du paragraphe
            while i < len(lines):
                current_line = lines[i].rstrip('\n')
                
                # Arrêter si ligne vide ou début d'un autre élément
                if not current_line.strip():
                    break
                if (current_line.startswith('#') or 
                    current_line.startswith('- ') or 
                    current_line.startswith('* ')):
                    break
                
                paragraph_lines.append(current_line)
                i += 1
            
            # Traiter les lignes du paragraphe
            for j, p_line in enumerate(paragraph_lines):
                p_line = parse_inline_formatting(p_line)
                if j == 0:
                    html_content.append(p_line)
                else:
                    html_content.append('<br/>')
                    html_content.append(p_line)
            
            html_content.append('</p>')
            continue
        
        i += 1
    
    # Écrire le fichier HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content) + '\n')


def main():
    """Fonction principale"""
    
    # Vérifier le nombre d'arguments
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    html_file = sys.argv[2]
    
    # Vérifier si le fichier Markdown existe
    if not os.path.exists(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)
    
    # Convertir le fichier
    convert_markdown_to_html(markdown_file, html_file)
    
    # Sortir avec le code 0 (succès)
    sys.exit(0)


if __name__ == "__main__":
    main()
