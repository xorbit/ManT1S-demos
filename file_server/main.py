from microdot import Microdot, Request, send_file
import asyncio
import os

# Allow large files to be sent
Request.max_content_length = 4 * 1024 * 1024

# Create Microdot web server object
app = Microdot()


# Make directory, ensuring all lower levels are created
def mkdirp(path: str) -> None:
    tail = ''
    try:
        head, tail = path.rsplit('/', 1)
        if head:
            mkdirp(head)
    except:
        pass
    try:
        os.mkdir(path)
    except:
        pass

@app.get('')
@app.get('/')
@app.route('/<path:path>', ['GET', 'PUT'])
async def update_file_handler(req, path=None):
    # Directory traversal is not allowed
    if path is not None and '..' in path:
        return "Directory traversal not allowed", 403
    # The file name in local storage
    file_name = req.path
    if req.method == 'PUT':
        # PUT: An update file is sent
        try:
            # Ensure the directory for the file exists
            mkdirp(file_name.rsplit('/', 1)[0])
            # Open the file for writing
            with open(file_name, 'wb') as f:
                # Write streamed chunks until full length received
                length = 0
                while length < req.content_length:
                    chunk = await req.stream.read(2048)
                    f.write(chunk)
                    length += len(chunk)
            return "File upload successful"
        except:
            return "Data save error", 503
    else:
        # GET: send the requested file
        # Make sure it exists
        try:
            # Is it a directory?
            if os.stat(file_name)[0] & 0x4000:
                # Init return object
                ret = {
                    'files': [],
                    'directories': []
                }
                # Get directory listing
                for name, ftype, inode, size in list(os.ilistdir(file_name)):
                    # Is it a directory?
                    if ftype & 0x4000:
                        # Add to directories
                        ret['directories'].append(name)
                    else:
                        # Add to files
                        ret['files'].append((name, size))
                # Append filesystem size info
                bsize, frsize, blocks, free, _, _, _, _, _, _ = \
                                                    os.statvfs(file_name)
                ret['size'] = frsize * blocks
                ret['free'] = bsize * free
                # Return the listing
                return ret
            else:
                # Send the file
                return send_file(file_name)
        except:
            # Doesn't exist
            return "File not found", 404

# Guard to allow import as module
if __name__ == "__main__":
    asyncio.run(app.start_server(port=80))

