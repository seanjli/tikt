import random
import string
from random import randint
from classes import Problem 
import sqlite3
import os

def make_test(name, prob_num):

    with sqlite3.connect("aime.db") as conn:
        
        c = conn.cursor()
        trycount = 0

        while True:
            
            trycount += 1

            ids = []
            problems = []

            while len(problems) < int(prob_num/5):
                c.execute("""SELECT * FROM aime WHERE 
                        Tags LIKE '% 0C%' OR
                        Tags LIKE '% 5C%' OR
                        Tags LIKE '% 10C%' OR   
                        Tags LIKE '% 15C%' OR
                        Tags LIKE '% 20C%'""")
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

            while len(problems) < int(2*prob_num/5):
                c.execute("""SELECT * FROM aime WHERE 
                        Tags LIKE '% 15C%' OR
                        Tags LIKE '% 20C%' OR
                        Tags LIKE '% 25C%'""")
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

            while len(problems) < int(3*prob_num/5):
                c.execute("""SELECT * FROM aime WHERE
                        Tags LIKE '% 25C%' OR
                        Tags LIKE '% 30C%' OR
                        Tags LIKE '% 35C%'""")
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

            while len(problems) < int(4*prob_num/5):
                c.execute("""SELECT * FROM aime WHERE
                        Tags LIKE '% 30C%' OR
                        Tags LIKE '% 35C%' OR
                        Tags LIKE '% 40C%'""")
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
                        Tags LIKE '% 40C%' OR
                        Tags LIKE '% 45C%' OR
                        Tags LIKE '% 50C%'""")
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
            
            if sum(diff_list) > 30*prob_num:
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

            break

        print([prob.subject + str(prob.diff) for prob in problems])
        print(trycount)

        problemarea = ""
        answerarea = ""

        for prob in problems:
            problemarea = problemarea + "\n \\item " + prob.statement + "\n" 
            answerarea = answerarea + "\n \\item $" + prob.answer + "$." + " Source: " + prob.title + "\n \n Solution: \\url{" + prob.link + "}"

        doc = """
    \\documentclass[11pt]{article}
    \\usepackage[roman,nocolor]{sean}
    \\usepackage{von}
    \\titledef{"""+name+"""\\\\
            \large Made with TiKT}
    \\authordef{Sean Li}
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

    \\end{document}
    """

        f = open("output.tex", "w")
        f.write(doc)
        f.close()

        key = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(8))

        os.system("latexmk output.tex")
        os.system("mv output.pdf " + key + ".pdf")
        os.system("rm output*")
        os.system("mv " + key + ".pdf static/tests/")

        return key
