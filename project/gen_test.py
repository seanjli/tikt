from _config import DATABASE
import random
import string
from random import randint
from classes import Problem 
import sqlite3
import os

def make_test(name, author, prob_num, min_diff, max_diff):

    with sqlite3.connect(DATABASE) as conn:
        
        c = conn.cursor()
        trycount = 0

        while True:
            
            trycount += 1

            ids = []
            problems = []

            while len(problems) < int(prob_num/3):
                c.execute("""SELECT * FROM aime WHERE
                    diff >= {} AND
                    diff <= {}""".format(min_diff, int(0.66*min_diff + 0.33*max_diff)))
                # WARNING SQL INJECT TODO
                probinfos = c.fetchall()
                probinfo = probinfos[randint(0,len(probinfos)-1)]
                if probinfo[0] not in ids:
                    problems.append(Problem(
                        probinfo[0],
                        probinfo[1],
                        probinfo[2],
                        probinfo[3],
                        probinfo[4],
                        probinfo[5],
                        probinfo[6],
                        probinfo[7]
                    ))
                    ids.append(probinfo[0])

            while len(problems) < int(2*prob_num/3):
                c.execute("""SELECT * FROM aime WHERE
                    diff >= {} AND
                    diff <= {}""".format(int(0.66*min_diff+0.33*max_diff), int(0.25*min_diff + 0.75*max_diff)))
                # WARNING SQL INJECT TODO
                probinfos = c.fetchall()
                probinfo = probinfos[randint(0,len(probinfos)-1)]
                if probinfo[0] not in ids:
                    problems.append(Problem(
                        probinfo[0],
                        probinfo[1],
                        probinfo[2],
                        probinfo[3],
                        probinfo[4],
                        probinfo[5],
                        probinfo[6],
                        probinfo[7]
                    ))
                    ids.append(probinfo[0])

            while len(problems) < prob_num:
                c.execute("""SELECT * FROM aime WHERE
                    diff >= {} AND
                    diff <= {}""".format(int(0.25*min_diff+0.75*max_diff), max_diff))
                # WARNING SQL INJECT TODO
                probinfos = c.fetchall()
                probinfo = probinfos[randint(0,len(probinfos)-1)]
                if probinfo[0] not in ids:
                    problems.append(Problem(
                        probinfo[0],
                        probinfo[1],
                        probinfo[2],
                        probinfo[3],
                        probinfo[4],
                        probinfo[5],
                        probinfo[6],
                        probinfo[7]
                    ))
                    ids.append(probinfo[0])

            problems.sort(key=lambda x: x.diff)
            
            diff_list = [prob.diff for prob in problems]
            
            if sum(diff_list) > (0.4*min_diff+0.6*max_diff)*prob_num:
                continue

            subj_list = [prob.subject for prob in problems[0:int(prob_num/3)]]
            count = [subj_list.count('A'), subj_list.count('C'), subj_list.count('G'), subj_list.count('N')]
            if not (max(count) - min(count) <= 2):
                continue


            subj_list = [prob.subject for prob in problems[int(prob_num/3):int(2*prob_num/3)]]
            count = [subj_list.count('A'), subj_list.count('C'), subj_list.count('G'), subj_list.count('N')]
            if not (max(count) - min(count) <= 2):
                continue


            subj_list = [prob.subject for prob in problems[int(2*prob_num/3):prob_num]]
            count = [subj_list.count('A'), subj_list.count('C'), subj_list.count('G'), subj_list.count('N')]
            if not (max(count) - min(count) <= 2):
                continue

            subj_list = [prob.subject for prob in problems]
            count = [subj_list.count('A'), subj_list.count('C'), subj_list.count('G'), subj_list.count('N')]
            if not (min(count) >= int(prob_num/5)):
                continue

            if (trycount > 200):
                print("Error: restrictions cannot be satisfied.")

            break

        print([prob.subject + str(prob.diff) for prob in problems])
        print(trycount)

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
