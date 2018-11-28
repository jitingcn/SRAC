

## docker
```
docker build -t srac:latest .
docker run -it -v $(pwd):/usr/workspace srac:3.7 sh
cd /usr/workspace/
chmod +x lightnovel_epub.py
./lightnovel_epub.py
```
If you face error when build dockerfile:
```dpkg: error: error creating new backup file '/var/lib/dpkg/status-old': Invalid cross-device link```

Run `echo N | tee /sys/module/overlay/parameters/metacopy` in host.

`bash -c "cd /usr/workspace && ./lightnovel_epub.py"`