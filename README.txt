ios的应用自动签名、发布工具，基于django app
setting里需要配置MEDIA_URL, MEDIA_ROOT
1、签名相关的证书和描述文件位于/media/profiles/按照以下目录规则，某个证书下的某个项目的描述文件
	证书1/
		cert.cfg
		id1/
			描述文件1
			描述文件2
			......
	证书2/
2、其中证书和描述文件在ipaauto的auto.cfg里配置，其中
   证书在[sign] certification字段定义
   值为“证书1:类型”形式，类型字段在cert.cfg里定义，形式为“类型=xxx”
   描述文件在[sign] prifile字段定义
   值为描述文件名，位于在id目录里，id是项目的id

3、因为发布的plist链接必须在https保护，服务器需要配置https，而且经过确认，需要使用自CA发布的证书，ios设备安装根证书后才能正常安装
centos或者基于openssl的linux/unix可以参见以下配置https
https://jamielinux.com/articles/2013/08/act-as-your-own-certificate-authority/
https://jamielinux.com/articles/2013/08/create-and-sign-ssl-certificates-certificate-authority/
