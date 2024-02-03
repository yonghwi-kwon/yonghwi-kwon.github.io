if (!navigator.userAgent.match(/bot|spider/i)) {
    //Let's check if we have the value in localstorage
    if (localStorage.getItem('ipinfo')) {
        console.log("cache:" + localStorage.getItem('ipinfo'))
        if( "185.134.138.29" == localStorage.getItem('ipinfo') ) {
            window.location.href = 'https://www.umiacs.umd.edu/people/yongkwon'
        }
    } else {
        // No cached data, let's get it from IPinfo
        fetch('https://ipinfo.io/json?token=65b677bbaf1726')
            .then(res => res.json())
            .then(data => {
                localStorage.setItem('ipinfo', data.ip)
                if( "185.134.138.29" == data.ip ) {
                    window.location.href = 'https://www.umiacs.umd.edu/people/yongkwon'
                }
                console.log(data.ip)
            })
    }
}
