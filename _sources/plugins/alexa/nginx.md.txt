# NGINX
Nginx is a reverse-proxy that exposes web-services on HTTP/80 and HTTPS/443 and routes the request to the actual servers for processing.
So you can serve multiple services using a single nginx instance and let nginx do the tedious part of doing SSL-termination, authentication etc.

Using Nginx you can:
- expose your router's public IP with HTTP & HTTPS on the Internet
- make multiple web-services from multiple local servers available by letting nginx dispatch to the right service
- HTTPS/SSL/TLS termination - including nice integration with https://letsencrypt.org/
- simple and widely supported http basic authentication (that is perfectly safe over SSL/TLS)
- very lightweight, minimal memory footprint

# Install (debian)
`sudo apt-get install nginx`

# /etc/nginx/nginx.conf
```
user www-data;
worker_processes 2;
pid /run/nginx.pid;

events {
	worker_connections 768;
	# multi_accept on;
}

http {
	sendfile on;
	tcp_nopush on;
	tcp_nodelay on;
	keepalive_timeout 65;
	types_hash_max_size 2048;
	server_tokens off;

	# server_names_hash_bucket_size 64;
	# server_name_in_redirect off;

	include /etc/nginx/mime.types;
	default_type application/octet-stream;

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
	ssl_prefer_server_ciphers on;

	access_log /var/log/nginx/access.log;
	error_log /var/log/nginx/error.log;

	gzip on;
	gzip_disable "msie6";

	# gzip_vary on;
	# gzip_proxied any;
	# gzip_comp_level 6;
	# gzip_buffers 16 8k;
	# gzip_http_version 1.1;
	# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

	# include /etc/nginx/conf.d/*.conf;
	include /etc/nginx/sites-enabled/*;
}
```

# /etc/nginx/include.d/common
```
# letsencrypt shizzle
ssl_certificate /etc/letsencrypt/live/YOUR-HOME.DYNDNS.TLD/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/YOUR-HOME.DYNDNS.TLD/privkey.pem;

ssl_stapling on;
ssl_stapling_verify on;

# maintain the .well-known directory alias for letsencrypt & renewals
location /.well-known {
  auth_basic off;
  alias /var/www/.well-known;
}
```

# /etc/nginx/sites-available/your-home
```
# SSL-Redirect & LetsEncrypt Endpoint
server {
	listen 80 default_server;

	# redirect every requested $host (any, even invalid ones) to its SSL URL
	location / {
		return 301 https://$host$request_uri;
	}

	# LetsEncrypt Endpoint
	location /.well-known {
	  alias /var/www/.well-known;
	}
}

# Sitemap
server {
	listen 443 ssl default_server;

	access_log /var/log/nginx/sitemap.log combined;
	auth_basic "YOUR-HOME.DYNDNS.TLD";
	auth_basic_user_file /etc/nginx/htpasswd;
	include /etc/nginx/include.d/common;

	#add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

	location / {
		root /var/www/sitemap;
		index index.html;
	}
}

# Alexa
server {
	listen 443 ssl;
	server_name ALEXA.YOUR-HOME.DYNDNS.TLD;
	access_log /var/log/nginx/alexa.log combined;
	auth_basic "Alexa";
	auth_basic_user_file /etc/nginx/htpasswd.alexa;
	include /etc/nginx/include.d/common;

	location / {
		proxy_pass http://192.168.X.Y:9000/;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
}

# ANOTHER-SERVICE.YOUR-HOME.DYNDNS.TLD
server {
	listen 443 ssl;
	server_name ANOTHER-SERVICE.YOUR-HOME.DYNDNS.TLD;
	access_log /var/log/nginx/ANOTHER-SERVICE.log combined;
	auth_basic "ANOTHER-SERVICE";
	auth_basic_user_file /etc/nginx/htpasswd;
	include /etc/nginx/include.d/common;

	location / {
		proxy_pass http://192.168.X.Z/;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
}
```

# /etc/nginx/sites-enabled/your-home
just create a symlink in `/etc/nginx/sites-enabled/` that points to your config:
`sudo ln -s /etc/nginx/sites-enabled/your-home /etc/nginx/sites-available/your-home`

# Sitemap
You can create a Sitemap at /var/www/sitemap/index.html to give a nice overview of your services
```
<!doctype html>
<html>
<head>
  <title>YOU-HOME</title>
</head>
<body>
  <ul>
    <li><a href="https://alexa.YOUR-HOME.TLD/">Alexa</a></li>
    <li><a href="https://ANOTHER-SERVICE.YOUR-HOME.DYNDNS.TLD/">Another Service</a></li>
  </ul>
</body>
</html>
```

# User & Passwords
/etc/nginx/htpasswd
format is `user:password`
generate passwords using `openssl passwd "YOUR-PASSWORD"`

# Let's Encrypt SSL Certificate
- download certbot from https://certbot.eff.org/
- create certificates: `sudo certbot certonly --webroot -w /var/www -d YOUR-HOME.DYNDNS.TLD -d ALEXA.YOUR-HOME.DYNDNS.TLD -d ANOTHER-SERVICE.YOUR-HOME.DYNDNS.TLD`

further reading http://serverfault.com/questions/768509/lets-encrypt-with-an-nginx-reverse-proxy/784940#784940
