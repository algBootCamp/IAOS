- mac中python pip安装 xxx 出错error: command 'clang' failed with exit status 1的解决办法:\
export ARCHFLAGS="-arch x86_64"
然后再次安装 xxx 即可。