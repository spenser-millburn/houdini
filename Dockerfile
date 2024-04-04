FROM alpine

RUN apk add --no-cache bc

CMD echo "scale=16; a(1)*4" | bc -