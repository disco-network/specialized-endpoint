# Overview

This project uses the Django Framework. Using Django slang, this project consists of two apps: `xtreem` and `xtreembackend` (corresponding to the directories with these names).

`xtreem` contains the Django project settings file (and the `urls.py` which is the entry point for request routing and which delegates to the `urls.py` of `xtreembackend`), whereas `xtreembackend` contains all of the actual code.

# Data parsing and serialization

A huge pain when working with client-server architectures is the parsing and serializing logic associated to the client-server communication. Each request is serialized by the client and parsed by the server. After that, the server processes the request and serializes its response, which in turn is parsed by the client.

To separate this concern from the domain logic, the `dataspecs` module is a framework for the specification of data types, which can then be serialized and parsed automatically during runtime. The module should take care that an exception is thrown if the parsed string does not satisfy the specification of the object.

Important examples of data types are primitive types (see `dataspecs`), domain objects (see `domain`), and request objects (see `api`).
