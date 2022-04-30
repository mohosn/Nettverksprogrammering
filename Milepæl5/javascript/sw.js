const cacheName = 'v1.0';

self.addEventListener("install", (ev) => {
    console.log("in install")
    ev.waitUntil(
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
    ev.waitUntil(
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
    console.log('Fetch event for ', event.request.url, ' ', event.request.method);
    event.respondWith(caches.open(cacheName).then((cache) => {
        // Go to the network first
        return fetch(event.request).then((fetchedResponse) => {
            if(event.request.method=="GET"){
                cache.put(event.request.url, fetchedResponse.clone());
            }
            return fetchedResponse;
        }).catch(() => {
            // If the network is unavailable, get
            return cache.match(event.request.url);
        });
    }));



})





