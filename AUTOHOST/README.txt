CYKA BLYAT


We have a hypothesis here that, certain domains reveal certain things, therefore we target the subset of resolved domains first
Because we could do all at once - see below

Basically man, you can't just assume seeing every IP as an IP that is worthy
Test the IPs that tell you something first, then everything else

THEN if nothing comes from a special service scan, do nmap -Pn -sV

-------------------------------------------------------------------------------------------
Above Meta Deprecated
-------------------------------------------------------------------------------------------

Run 1NMAPSonic.py
  Yield: IP, Maybe DNS Reso, Ports, Services

Utilize Software Versioning Commands from jsons like /HOSTCONTACT or in /HostOperations
This will be deprecated.
-------------------------------------------------------------------------------------------
Above Meta Deprecated
-------------------------------------------------------------------------------------------

Run 1NMAPSonic.py 
  Yield: IP, Maybe DNS Reso, Ports, Services

Make Python script to lever ServiceProbe1.file, ServiceProbe2.file, serviceprobelow.file (all json, playa)
Make Service probes for items in PopularRevProxies.json, reverseProxy1-2.json files

Hypo(Run ServiceProbeScanner.py)
  - Reads: IP, Ports, values from 
      ServiceProbe1.file, ServiceProbe2.file, serviceprobelow.file
      Service probes for items in PopularRevProxies.json, reverseProxy1-2.json
  - Sends service probes in jsons read to services that match the Ports in the given JSON Item of the IP in iteration

This will be deprecated. Soon
-------------------------------------------------------------------------------------------
Above Meta Deprecated
-------------------------------------------------------------------------------------------

Run 1NMAPSonic.py
  Yield: IP, DNS Reso, Ports, Services

Run 2ServiceProbeAuto.py IPBank.json /Path/To/Service/Probe/Directory

TODO - Make a Script to then scan services, and do curl for Common, Undes'd, endpoints from HOSTCONTACT/some.json file - like objectively you know what I mean fella you know which one just make sure you orient and organize it.

HosterJSONFull, PopularRevProxies.json, reverseProxy1.json, reverseProxy2.json 
Basically the same script you made "2ServiceProbeAuto.py" IPBank.json /Path/To/Endpoints/Test/Bank/Directory

Visualize:
Run DeepSeekGUI.py or ClaudeGUI.py

-------------------------------------------------------------------------------------------
Above Meta Deprecated
-------------------------------------------------------------------------------------------

Run 1NMAPSonic.py
  Yield: IP, DNS Reso, Ports, Services

Run 2ServiceProbeAuto.py IPBank.json /Path/To/Service/Probe/Directory

Run 3EndpointScanner.py IPBank.json /Path/To/Services/And/Endpoints/Directory
