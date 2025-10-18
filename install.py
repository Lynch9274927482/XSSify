import os,sys,subprocess
p=['requests>=2.31.0','beautifulsoup4>=4.12.0','flask>=3.0.0','colorama>=0.4.6','lxml>=4.9.0']
for i in p:
    print('installing',i,'...')
    try:
        subprocess.check_call([sys.executable,'-m','pip','install',i])
    except:
        print('uhh failed on',i)
print('done lol')
