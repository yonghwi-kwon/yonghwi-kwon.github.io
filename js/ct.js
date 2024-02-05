if (!navigator.userAgent.match(/bot|spider/i)) {
    const iparray = ["185.134.138.29", "185.134.138.34", "136.23.7.213"]
    if (localStorage.getItem('ipinfo') && localStorage.getItem('ipregion') && localStorage.getItem('iporg')) {        
        ip = localStorage.getItem('ipinfo');
        region = localStorage.getItem('ipregion');
        org = localStorage.getItem('iporg');
        for (let i = 0; i < iparray.length; i++) {
            if ( ip == iparray[i] ) { window.location.href = 'https://www.umiacs.umd.edu/people/yongkwon'; break; }
        }
        if ( ip.indexOf("136.23.7.") == 0 && region == "Berlin" && org.indexOf("Google, LLC") != -1 ) { // gvpn
            window.location.href = 'https://www.umiacs.umd.edu/people/yongkwon';
        }
    } else {
        fetch('https://ipinfo.io/json?token=65b677bbaf1726')
            .then(res => res.json())
            .then(data => {
                ip = data.ip;
                region = data.region;
                org = data.org;                
                localStorage.setItem('ipinfo', ip);
                localStorage.setItem('ipregion', region);
                localStorage.setItem('iporg', org);

                for (let i = 0; i < iparray.length; i++) {
                    if ( ip == iparray[i] ) { window.location.href = 'https://www.umiacs.umd.edu/people/yongkwon'; break; }
                }
                if ( ip.indexOf("136.23.7.") == 0 && region == "Berlin" && org.indexOf("Google, LLC") != -1 ) { // gvpn
                    window.location.href = 'https://www.umiacs.umd.edu/people/yongkwon';
                }
                //console.log(data)
            })
    }
}
