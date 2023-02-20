# app运行脚本
./initenv.sh
export FLASK_APP=../app/app
#flask run --reload --debugger -p 8888
# reload：热加载  debugger：debug模式
#flask run --reload -p 8888
flask run -h 127.0.0.1 -p 8888