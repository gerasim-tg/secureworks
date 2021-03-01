import requests
import time
import os, sys
from subprocess import PIPE, run

url = "http://localhost:8080/sample/command.jsp"
def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

def generate_not_unique(num, path):
    pids = []
    start = round(time.time() * 1000)
    for i in range(0, num):
        ## only one file
        filename = 'testfile.txt'
        payload = [{'cmd': f'touch {filename}'},
                   {'cmd': f'rm {filename}'}
                   ]
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = {
            'Cookie': f'custom_pytest_{i}'}
        # create a file
        response = response = requests.post(url, headers=headers, cookies=cookies, data=payload[0])
        assert response.status_code == 200, f"Unexpected status code {response.status_code}"
        time.sleep(0.2)
        os.system(f"open {path}{filename}")
        pid = out("pgrep TextEdit")
        print(f"pid: {pid}")
        if pid not in pids:
            pids.append(pid)
            print(f"appended {pid}")

    print(f'Unique pids: {len(pids)}')
    # kill the process
    os.system('bash -c "exec pkill -f TextEdit"')
    # remove the file
    response = requests.post(url, headers=headers, cookies=cookies, data=payload[1])
    time.sleep(0.1)
    assert response.status_code == 200, f"Unexpected status code {response.status_code}"


def generate_unique_procs(num, tomcat_path):
    # tomcat_path = "/usr/local/Cellar/tomcat/9.0.39/libexec/"
    pids = []
    start = round(time.time() * 1000)
    for i in range(0, num):
        ## each request will use unique file name
        filename = f'testfile_0{i}.txt'

        payload = [{'cmd': f'touch {filename}'},
                   {'cmd': f'rm {filename}'}
                   ]
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = {
            'Cookie': f'custom_pytest_{i}'}

        response = requests.post(url, headers=headers, cookies=cookies, data=payload[0])
        assert response.status_code == 200, f"Unexpected status code {response.status_code}"
        time.sleep(0.2)
        print(f'generated {filename}')
        os.system(f"open  {tomcat_path}{filename}")
        pid = out("pgrep TextEdit")
        if pid not in pids:
            pids.append(pid)
            print(f"appended {pid}")
        # kill the process
        os.system('bash -c "exec pkill -f TextEdit"')
        # remove the file
        response = requests.post(url, headers=headers, cookies=cookies, data=payload[1])
        time.sleep(0.1)
        assert response.status_code == 200, f"Unexpected status code {response.status_code}"

    print(f'Unique pids: {len(pids)}')
    end = round(time.time() * 1000)
    elapsed_time = end - start
    print(f"Done in {elapsed_time} ms, created {len(pids)} unique processes")

def main():
    # total arguments
    n = len(sys.argv)
    if len(sys.argv) and sys.argv[1] in ("-h", "--Help"):
        print("Diplaying Help")
        print("pass  U for unique, N = for not unique\n"
                    " - num of unique processes to generate\n"
                    " - path to your tomcate exec directory\n")
    print("Total arguments passed:", n)
    # Arguments passed
    print("\nArguments passed:", end=" \n")
    if n < 4:
        exit("incorrect args list")
    for i in range(1, n):
        print(sys.argv[i], end=" ")
        test_name = sys.argv[1]
        num = sys.argv[2]
        tomcat_path = sys.argv[3]

    return (test_name, num, tomcat_path)

if __name__ == "__main__":
    test_name, num, tomcat_path  = main()
    if "U" in test_name:
        generate_unique_procs(int(num), tomcat_path)
    else:
        generate_not_unique(int(num), tomcat_path)

