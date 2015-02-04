# simple-multidevice-auth

Online authentication usually requires an account on the service you're trying to authenticate on. In some scenarios, this isn't necessary and overcomplicates things, for example when building a colloborative text editing or a synchronized todo list application. You want to be able to use one "session" from multiple devices (maybe with multiple users, too), but don't care so much about security and really don't want to remember your credentials every time you use it.

For this purpose, I introduce simple-multidevice-auth (non-final name), which is supposed to work like this: A client can either request a new session from the server or try to participate in an existing one. When it creates a new session, it can then generate "tokens" that allow other devices to participate in the session. Participating requires a valid session id plus a valid token (which might be a very simple one, as it could be limited in time). The token could also be displayed in a different way, e.g. though a QR code when using a mobile device. Every token can only be used once, so that using it by visiting a URL is sort-of safe.

simple-multidevice-auth requires a compatible server and client that speak the same protocol:

## Protocol

All non-data actions are initiated by the client only, which means a server can be implemented in a simple LAMP environment (i.e. in PHP). All communication is done in JSON.

### Creating a session

A session consists of a session id, a list of authorized user ids, and a list of active tokens with an expiration timestamp, all of which (except for the timestamp, of course) are pseudorandom and unique to the session. A session id could also be non-random.

Client:

    {
        "action": "new"
    }

Server:

    {
        "status": "ok",
        "session": "7a33fceb",
        "user": "f648daf2"
    }

Client:

    {
        "action": "push",
        "data": "..."
        "session": "7a33fceb",
        "user": "f648daf2"
    }

Server:

    {
        "status": "ok",
    }

Client:

    {
        "action": "add-client",
        "session": "7a33fceb",
        "user": "f648daf2"
    }

Server:

    {
        "status": "ok",
        "token": "55148",
        "timeout": "1422982970",
        "session": "7a33fceb"
    }

Client 2:

    {
        "action": "join",
        "session": "7a33fceb",
        "token": "55148"
    }

Server:

    {
        "status": "ok",
        "session": "7a33fceb",
        "user": "88228b2"
    }

Client 2:

    {
        "action": "pull",
        "session": "7a33fceb",
        "user": "88228b2"
    }

Server:

    {
        "status": "ok",
        "data": "..."
    }

Client 3:

    {
        "action": "pull"
    }

Server:

    {
        "status": "fail",
        "error": "not authenticated"
    }

## Security

This system is not intended to be used in environments requiring real security. You can make it sort-of safe by using TLS. Apart from that, no encryption is used.
