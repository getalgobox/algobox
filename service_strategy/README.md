# Algo service

This service keeps track of algorithms in play, it allows CRUD operations against them and provides an API for accessing those operations.

It is also responsible for executing algorithms with relevant contexts once some new data is received.

# todo

- [ ] We need to change the way we are generating sessions. Right now,
  we're using the session maker from models. This should be moved somewhere which will allow us to toggle which connection string is used. This is because of testing with testcontainers. In the future, the connection string may be different or unpredictable. 
