const cacheName = 'v1.0'; //name of cache  random

self.addEventListener("install", (event) => {  //cache static files 
    console.log("in install") 
    event.waitUntil(
        caches
            .open(cacheName)
            .then(cache => {
                console.log("caching file")
                cache.addAll([
                    './',
                    './ui.html',
                    './script.js',
                    './style.css',
                    './gruppe11-xml.xml',
                    './gruppe11-xml.css',
                    './index.html',
                    './style-main.css',
                    ]
                )
            }).then(() => {
                self.skipWaiting();
            })
    )

})

self.addEventListener("activate", (ev) => {
    console.log("in activate")
    //removing unwanted caches 
    ev.waitUntil(  //deleting old cache if you change the name of the cache
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cache => {
                        if (cache != cacheName) {
                            console.log("Clearing old cache");
                            return caches.delete(cache);
                        }

                    })
                )
            })
    )
})

self.addEventListener("fetch", (event) => {

    console.log('Fetch event for ', event.request.url, ' ', event.request.method);  //network first caching method
    event.respondWith(caches.open(cacheName).then((cache) => {
        // Go to the network first
        console.log(event.request);
        return fetch(event.request).then((fetchedResponse) => {
            if(event.request.method=="GET"){
                cache.put(event.request.url, fetchedResponse.clone()); //saving the Get method response in the cache (eg view all poem, view poem by id, view own poem)
            }
            return fetchedResponse;
        }).catch(() => {
            // If the network is unavailable, get
            return cache.match(event.request.url);
        });
    }));



})


