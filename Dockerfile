FROM alpine

RUN apk add --no-cache bc

CMD echo "scale=16; 4*a(1)" | bc -