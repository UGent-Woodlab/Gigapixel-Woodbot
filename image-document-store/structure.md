# MongoDB structure

Structure to store a image in datastore

```json
{
    startX: 0.0, 
    startY: 0.0,
    incrementX: 0.5,
    incrementY: 0.5,
    sources: [
        [{}, {startZ: 0.0, incrementZ: 0.05, sources: ["path1", "path2"] }, {startZ: 0.0, incrementZ: 0.05, sources: ["path1", "path2"]}],
        [{startZ: 0.0, incrementZ: 0.05, sources: ["path1", "path2"] }, {startZ: 0.0, incrementZ: 0.05, sources: ["path1", "path2"]}. {}],

    ]
}
```

