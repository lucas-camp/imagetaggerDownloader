### Compile latest .proto file

The latest .proto file is located in `$NDevils2015Root/src/Tools/Protobuf`.
See also the Wiki entry for protobuf.

To compile it run the following command inside this directory.



```
protoc -I=. --python_out=. imageLabelData.proto
```