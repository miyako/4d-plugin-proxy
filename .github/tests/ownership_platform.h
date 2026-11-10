#import <Carbon/Carbon.h>
#import <Cocoa/Cocoa.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include "proxy.h"

// Forced into every translation unit before the actual plugin and complete SDK.
@interface OwnershipURL : NSObject
- (id)initWithString:(NSString *)value;
- (NSString *)absoluteString;
@end
@interface OwnershipImage : NSObject
- (id)initWithCGImage:(CGImageRef)image size:(NSSize)size;
- (NSData *)TIFFRepresentation;
@end
CFURLRef OwnershipCreateURL(CFAllocatorRef, CFStringRef, CFURLPathStyle, Boolean);
CFStringRef OwnershipCopyPath(CFURLRef, CFURLPathStyle);
pxProxyFactory *OwnershipFactoryNew();
void OwnershipFactoryFree(pxProxyFactory *);
char **OwnershipGetProxies(pxProxyFactory *, const char *);
void OwnershipFreeProxies(char **);

#define NSURL OwnershipURL
#define NSImage OwnershipImage
#define CFURLCreateWithFileSystemPath OwnershipCreateURL
#define CFURLCopyFileSystemPath OwnershipCopyPath
#define px_proxy_factory_new OwnershipFactoryNew
#define px_proxy_factory_free OwnershipFactoryFree
#define px_proxy_factory_get_proxies OwnershipGetProxies
#define px_proxy_factory_free_proxies OwnershipFreeProxies
