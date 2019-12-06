import requests
import json
import os
import time

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, "config.json"), "r") as f:
    config = json.load(f)


class JsonTestBot:
    def __init__(self, base_url):
        base_url = 'https://team.usetrace.com/rpc/app/init'
        self.r = requests.Session()
        self.results = []
        self.r.headers={
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': config["USER_AGENT"],
            #'User-Agent': USER_AGENT,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://team.usetrace.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Cookie': config["COOKIES"]
            #'Cookie': COOKIES
        }

        self.endpoints = {
            'init': f'{base_url}',
            'project': 'https://api.usetrace.com/api/project/',
        }

        self.project = Project(self)
        self._hidden = None


class Project:
    def __init__(self, bot):
        self._b = bot
        self._projects = self.all()

    def all(self):
        """Get all projects"""
        r = self._b.r.get(self._b.endpoints["init"]).json()
        data = r["projects"]
        return {i['id']: i for i in data}

    def names(self):
        projects = self.all()
        result = []
        for key in projects:
            item = projects[key]
            result.append(item["name"])
        return "\n".join(result)

    def run(self, arg1, arg2=None, arg3=None, arg4=None):
        input = arg1
        if arg2:
            input = input + " " + arg2
        
        if arg3:
            input = input + " " + arg3

        if arg4:
            input = input + " " + arg4

        projects = self.all()

        for key in projects:
            item = projects[key]

            if item["name"].lower() == input.lower():
                payload = {
                    "requiredCapabilities": [{"browserName": "chrome"}]
                }
                url = self._b.endpoints["project"]+ key + '/execute_all'
                headers = {"Content-type": "application/json"}
                project_run = requests.post(url, data=json.dumps(payload), headers=headers)

                result_url = "https://api.usetrace.com/api/results/"+project_run.text+"/xunit"

                i = 0
                status_code = 404
                while i < 3000 and status_code == 404:
                    time.sleep(3)
                    tmp_result = requests.get(result_url)
                    content = tmp_result.content.decode("utf-8") 
                    if "testsuite" in content:
                        status_code = 200
                    i+=1

                if status_code == 200:
                    final_result_url = self._b.endpoints["project"]+ key + '/lastBatchStatus'
                    final_project_run = requests.get(final_result_url).json()

                    report = []
                
                    if not final_project_run["batch"]:
                        return "no result yet"
                    
                    batch = final_project_run["batch"]

                    if project_run.text != batch["id"]:
                        return "something went wrong with the test, please try again later"

                    report.append("Name: " + item["name"])
                    report.append("Id: " + batch["id"])
                    report.append("Requested: " + str(batch["requested"]))
                    report.append("Finished: " + str(batch["finished"]))
                    report.append("Passed: " + str(batch["passed"]))
                    report.append("Failed: " + str(batch["failed"]))

                    if batch["failed"] > 0:
                        cnt = 1

                        # check browserSessions by batchId
                        init_data = self._b.r.get(self._b.endpoints["init"]).json()

                        browserSessions = init_data["browserSessions"]

                        # store scriptIds that need to match error message and screenshot
                        matchResultScripts = []

                        for browserSess in browserSessions:
                            if "batchId" in browserSess and "hasError" in browserSess and "scriptId" in browserSess:
                                if browserSess["batchId"] == batch["id"] and browserSess["hasError"]:
                                    matchResultScripts.append(browserSess["scriptId"])


                        change_url = "https://team.usetrace.com/rpc/project/" + key + "/changes"
                        change_results = self._b.r.get(change_url).json()

                        for cr in change_results:
                            if cr["scriptId"] in matchResultScripts and cr["capabilities"]["browserName"] == "chrome":
                                report.append("== Failure #" + str(cnt) + " ==")
                                cnt = cnt + 1
                                report.append(cr["traceLabel"])
                                report.append("Error Message:")
                                report.append(cr["errorMessage"])
                                report.append("Error Screenshot:")
                                report.append(cr["errorScreenshotUrl"])

                        if cnt-1 != batch["failed"]:
                            report.append("== Failed counts not match in report, additional investigation needed")
                    
                    return "\n".join(report)

                return project_run.text
        
        return "Invalid project name"

    def result(self, arg1, arg2=None, arg3=None, arg4=None):
        input = arg1
        if arg2:
            input = input + " " + arg2
        
        if arg3:
            input = input + " " + arg3
        
        if arg4:
            input = input + " " + arg4

        projects = self.all()

        for key in projects:
            item = projects[key]
            if item["name"] == input:
                url = self._b.endpoints["project"]+ key + '/lastBatchStatus'
                project_run = requests.get(url).json()
                report = []
                
                if not project_run["batch"]:
                    return "no result yet"
                
                batch = project_run["batch"]
                report.append("Id: " + batch["id"])
                report.append("Requested: " + str(batch["requested"]))
                report.append("Finished: " + str(batch["finished"]))
                report.append("Passed: " + str(batch["passed"]))
                report.append("Failed: " + str(batch["failed"]))
                return "\n".join(report)

        return "Invalid project name"


# _entrypoint_ is the name of the root class botcannon and will load using
# a modified version of fire that can be used to call this file directly (see below).
_entrypoint_ = 'JsonTestBot'

if __name__ == '__main__':
    import fire

    fire.Fire(JsonTestBot)
