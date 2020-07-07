import os
import random
import string

def render_test(name, author, problems):
    problemarea = ""
    answerarea = ""
    sourcearea = ""

    for prob in problems:
        problemarea = problemarea + "\n \\item " + prob.statement + "\n" 
        answerarea = answerarea + "\n \\item $" + prob.answer + "$"
        sourcearea = sourcearea + "\n \\item \\textbf{Source}: " + prob.title + "\n \n \\textbf{Tags}: " + prob.tags + "\n \n \\textbf{Solution}: \\url{" + prob.link + "}"

    doc = """
\\documentclass[11pt]{article}
\\usepackage[roman,nocolor]{sean}
\\usepackage{von}
\\titledef{"""+name+"""\\\\
        \large Made with TiKT\\footnote{By Sean Li. Selected problems belong to their respective authors and oragnizations, as attributed.}}
\\authordef{"""+author+"""}
\\datedef{Generated \\today}
\\lheaddef{"""+name+"""}
\\rheaddef{Sean Li}
\\linespread{1}

\\begin{document}
\\maketitle

\\section{Problems}

\\begin{enumerate}""" + problemarea + """\\end{enumerate}

\\vfill

\\begin{flushright}
  \\emph{Time limit: 50 minutes.} \\\\
  \\emph{Each problem is worth one point.}
\\end{flushright}

\\newpage

\\section{Answers}

\\begin{enumerate}""" + answerarea + """\\end{enumerate}

\\newpage

\\section{Problem Info}

\\begin{enumerate}""" + sourcearea + """\end{enumerate}

\\end{document}
"""
    key = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(8))
    
    f = open("pre-" + key + ".tex", "w")
    f.write(doc)
    f.close()

    os.system("latexmk pre-" + key + ".tex")
    os.system("mv pre-" + key + ".pdf " + key + ".pdf")
    os.system("rm pre-" + key + "*")
    os.system("mv " + key + ".pdf static/tests/")

    return key
