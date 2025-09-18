# build a local system
export MARKER=`date +%s`

echo "this is build $MARKER"

docker build -f Dockerfile-dev . -t sadewiki:$MARKER 

echo "container built!"
echo "press Ctrl+C to exit the server, this will also kill the container"

docker run -p 8000:8000 -it sadewiki:$MARKER