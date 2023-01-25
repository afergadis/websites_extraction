# import shutil
# import glob
import os

# def_comd = r"java -jar ilsp-boilerpipe-1.9.1-jar-with-dependencies.jar -id 0 -od o\5"
def_comnd = r"java -jar ilsp-boilerpipe-1.9.1-jar-with-dependencies.jar"
webst_path =  r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\boilerplate_removal\out"
# webst_fldr =  r"out"
webst_fldr =  webst_path.split("\\")[-1]
boilpl_fold = 'clean_websites'

# find all folders corresponding to a website
os.chdir(r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\boilerplate_removal\out")
myBat = open(r'C:\Users\c.borovilou\Desktop\MSc\διπλωματική\boilerplate_removal\cmd_commands.bat','w+')
# for f_name in os.listdir("."):
i=0
for f_name in os.listdir("."):
    i +=1
    fin_comnd = def_comnd + ' -id ' + webst_fldr + "\\" + f_name + ' -od ' + boilpl_fold + "\\" + f_name + "\n"
    # with open('cmd_commands.bat', 'w') as f:
    myBat.write(fin_comnd)

myBat.close()
print('000')
