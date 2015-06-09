# synolopy

A very basic Python wrapper for *some* of the Synology APIs.

Note that this is not a fork from [Thavel's Synolopy](https://pypi.python.org/pypi/synolopy), I'm just too lazy to find another name.

## Start a download

```
ds = DownloadStationTask(
	'http://nas-ip:5000/webapi/',
	('username', 'password')
)
ds.login()
ds.create(uri="magnetlink / http / whatever")
ds.create(file="filepath")
ds.logout()
```
