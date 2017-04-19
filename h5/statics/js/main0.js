function weixin_share(i) {
    if (!(i && i.appid && i.noncestr && i.timestamp && i.signature)) return void console.error("wx_conf_is_error");
    var e = {
        title: i.share_title || "",
        desc: i.share_desc || "",
        link: i.share_link || "",
        imgUrl: i.share_img || "",
        trigger: function (i) {},
        success: function (i) {},
        cancel: function (i) {},
        fail: function (i) {}
    };
    wx.config({
        debug: !1,
        appId: i.appid,
        timestamp: i.timestamp,
        nonceStr: i.noncestr,
        signature: i.signature,
        jsApiList: ["onMenuShareTimeline", "onMenuShareAppMessage", "onMenuShareQQ", "onMenuShareQZone", "onMenuShareWeibo", "getNetworkType"]
    }),
    wx.error(function (i) {}),
    wx.ready(function () {
        wx.onMenuShareAppMessage(e),
        wx.onMenuShareTimeline(e),
        wx.onMenuShareQQ(e),
        wx.onMenuShareQZone(e);
        var i = Page;
        i.gConfig.ua.isWeixin && i.gConfig.ua.isIOS && (i.gConfig.isNeedOpenTip || (i.startPlay(), _hmt.push(["_trackEvent", "share", "video", "autoPlay"])))
    })
}!
function (i) {
    var e = !0;
    $.fn.show && ($.fn.show = function () {
        return $(this) && $(this).css("display", "block"),
        $(this)
    }, $.fn.hide = function () {
        return $(this) && $(this).css("display", "none"),
        $(this)
    });
    var t = {
        log: function (i) {
            if (e) {
                "object" == typeof i && (i = JSON.stringify(i));
                var t = "http://www.baidu.com/?debugMsg=-----" + i + "----" + (new Date).getTime();
                (new Image).src = t
            }
        },
        ua: function (i) {
            var e = {
                android: /android/i,
                iphone: /iphone/i,
                ipad: /ipad/i,
                ipod: /ipod/i,
                weixin: /micromessenger/i,
                mqq: /QQ\//i,
                app: /ingke/i,
                alipay: /aliapp/i,
                weibo: /weibo/i,
                chrome: /chrome\//i
            },
                t = {},
                n = window.navigator.userAgent;
            return i && i in e ? e[i].test(n) : ($.each(e, function (i, e) {
                    t[i] = e.test(n)
                }), t.ios = t.iphone || t.ipad || t.ipod, t.mobile = t.ios || t.android, t.pc = !t.mobile, window.chrome && window.chrome && (t.chrome = !0), t)
        },
        getQueryString: function (i, e) {
            var t = new RegExp("(^|&)" + i + "=([^&]*)(&|$)", "i"),
                n = window.location.search.substr(1).match(t);
            return null != n ? decodeURIComponent(n[2]) : e || ""
        },
        getQueryData: function (i, e) {
            var t = {},
                n = (e || location.href).split("?")[1];
            if (!n) return null;
            for (var o = n.split("&"), a = 0, s = o.length; a < s; a++) {
                    var r = o[a].split("="),
                        l = r[0],
                        c = r[1] || "";
                    l && (t[l] = decodeURIComponent(c))
                }
            return i ? t[i] : t
        },
        trace: function () {},
        storage: {
            get: function (i) {
                if (i) return window.sessionStorage ? sessionStorage.getItem(i) : void 0
            },
            set: function (i, e) {
                i && e && window.sessionStorage && sessionStorage.setItem(i, e)
            },
            del: function () {}
        },
        parseTemplate: function (i, e) {
            for (var t in i) e = e.replace(new RegExp("{" + t + "}", "g"), i[t] || "");
            return e
        }
    };
    t.getCookie = function (i) {
        var e, t = new RegExp("(^| )" + i + "=([^;]*)(;|$)");
        return e = document.cookie.match(t),
        e ? window.unescape ? window.unescape(e[2]) : e[2] : null
    },
    t.setCookie = function (i, e) {
        var t = new Date;
        t.setTime(t.getTime() + 2592e6),
        e = window.escape ? window.escape(e) : e;
        var n = location.host.split(".").slice(-2).join(".");
        n ? document.cookie = i + "=" + e + ";expires=" + t.toGMTString() + "; domain=" + n : document.cookie = i + "=" + e + ";expires=" + t.toGMTString()
    },
    t.delCookie = function (i) {
        var e = t.getCookie(i);
        void 0 !== e && (document.cookie = i + "=" + e + ";expires=" + new Date(0).toGMTString())
    },
    t.getData = function (i) {
        if (window.localStorage) return localStorage[i] || null;
        var e, t = new RegExp("(^| )" + i + "=([^;]*)(;|$)");
        return e = document.cookie.match(t),
        e ? window.unescape ? window.unescape(e[2]) : e[2] : null
    },
    t.setData = function (i, e) {
        if (window.localStorage) localStorage[i] = e;
        else {
            var t = new Date;
            t.setTime(t.getTime() + 2592e6),
            e = window.escape ? window.escape(e) : e,
            document.cookie = i + "=" + e + ";expires=" + t.toGMTString()
        }
    },
    t.delData = function (i) {
        var e = t.getData(i);
        void 0 !== e && (window.localStorage ? delete localStorage[i] : document.cookie = i + "=" + e + ";expires=" + new Date(0).toGMTString())
    },
    t.getScript = function (i, e) {
        var t = document.createElement("script");
        t.type = "text/javascript",
        t.src = i,
        document.getElementsByTagName("head")[0].appendChild(t),
        t.onload = t.onreadystatechange = function () {
            this.readyState && "loaded" !== this.readyState && "complete" !== this.readyState || "function" == typeof e && e()
        }
    },
    i.Util = t
}(window),


function (i) {
    var e = "//webapi.busi.inke.cn";
    e = location.href.indexOf("beta.www.ingkee.com") >= 0 || location.href.indexOf("beta.busi.inke.com") >= 0 ? "//beta.busi.ingkee.com" : location.href.indexOf(".a8.com") >= 0 || location.href.indexOf(".inke.cn") >= 0 ? "//webapi.busi.inke.cn" : location.href.indexOf(".151:777") >= 0 || location.href.indexOf("testweb") >= 0 ? "//101.201.28.151:666" : "//webapi.busi.inke.cn";
    var t = {
        ajax: function (i) {
            var i = i || {},
                t = e;
            return $.ajax({
                    url: i.url.indexOf("http") == -1 ? t + i.url : i.url,
                    data: i.data || {},
                    type: i.type || "get",
                    dataType: i.dataType || "json",
                    success: function (e) {
                        i.success && i.success(e)
                    },
                    error: function () {
                        i.error && i.error(),
                        console.error("api error url is ", i.url)
                    }
                })
        },
        log: function (i) {
            "object" == typeof i && (i = JSON.stringify(i));
            "http://www.baidu.com/?debugMsg=-----" + i + "----" + (new Date).getTime()
        },
        openApp: function () {},
        scaleImg: function (i) {
            var e = "http://image.scale.a8.com/imageproxy2/dimgm/scaleImage";
            return e + "?url=" + encodeURIComponent(i.url) + "&w=" + i.w + "&h=" + i.h + "&s=" + (i.s || 80)
        },
        trace: function (i) {
            var e = {
                click_id: "",
                click_pos: "",
                live_uid: "",
                live_id: "",
                live_status: "",
                share_uid: "",
                share_from: "",
                installed: "",
                pop: "",
                share_time: "",
                app_type: "",
                open_time: "",
                is_login: "",
                uid: ""
            },
                t = {
                    allloadtime: "",
                    imgloadtime: "",
                    load_type: "",
                    api_end: "",
                    video_status: "",
                    video_loadtime: "",
                    video_url: "",
                    app_type: Page.gConfig.ua.isIOS ? "ios" : "android"
                },
                n = {
                    connect_time: "",
                    is_connected: ""
                };
            if (i && i.report_type) {
                    var o = {
                        cc: "TG0012",
                        source: "",
                        page_code: "",
                        uid: "",
                        busi_code: "weixin_share",
                        report_type: "",
                        other: {},
                        time: parseInt((new Date).getTime()),
                        url: window.location.href,
                        _t: (new Date).getTime()
                    },
                        a = {};
                    "wechat_share" == i.report_type ? a = e : "qa" == i.report_type ? a = t : "sio" == i.report_type && (a = n),
                    o.other = a,
                    $.extend(!0, o, i || {}),
                    o.other = JSON.stringify(o.other);
                    var s = "https://service.busi.inke.cn";
                        (location.href.indexOf("testweb") >= 0 || location.href.indexOf(".151") >= 0) && (s = "//test.web.service.inke.com");
                    var r = s + "/web/click_report?" + $.param(o);
                    setTimeout(function () {
                            (new Image).src = r
                        })
                }
        }
    };
    i.Common = t
}(window);

!
function (i) {
    function e(i) {
        var e = "http://www.qq.com?c------=" + i + "&t=" + (new Date).getTime();
        (new Image).src = e,
        setTimeout(function () {}, 0)
    }
    function t(i) {
        if (i = parseInt(i) || 0, !i) return 0;
        var e = Math.floor(i / 3600),
            t = i % 3600,
            n = ("0" + Math.floor(t / 60)).substr(-2),
            o = ("0" + t % 60).substr(-2);
        e < 10 && (e = ("0" + e).substr(-2));
        var a = "";
        return e > 0 && (a += e + ":"),
        (e > 0 || n > 0) && (a += n + ":"),
        a += o
    }
    function n(i, e) {
        return this.opt = {
            width: innerWidth,
            height: innerHeight,
            file: "http://record2.inke.cn/record_1480314030249027/1480314030249027.m3u8?uid=0",
            controls: !1,
            autoStart: !0,
            image: "",
            status: 1,
            isNeedPause: !0,
            isNeedPoster: !0,
            isShowPoster: !0,
            isAutoPlay: !0,
            isNeedProcessBar: !0,
            isNeedPreload: !0,
            events: {
                onPlay: null,
                onPlaying: null,
                onTimeupdate: null,
                ondurationchange: null,
                onPause: null,
                onBuffer: null,
                onWaiting: null,
                onReady: null,
                onError: null,
                onSetupError: null,
                onComplete: null,
                onEnd: null,
                onIdle: null,
                onDisplayClick: null,
                onPosterShow: null
            }
        },
        this.isStartPlay = !1,
        this.isCanplay = !1,
        this.isWaiting = !1,
        this.state = "",
        this.hasPlayed = !1,
        $.extend(!0, this.opt, e || {}),
        1 == this.opt.status && (this.opt.isNeedPause = !1),
        this.video = null,
        this.processObj = null,
        this.init(i),
        this
    }
    function o(i, e) {
        "function" == typeof i && i(e)
    }
    n.prototype = {
        init: function (i) {
            var e = this;
            return e.$container = $(i),
            e.render(),
            e.processObj = this.renderProcess(),
            e.bindEvent(),
            e
        },
        render: function () {
            var i = this,
                e = i.opt,
                t = "width:" + e.width + "px; height:" + e.height + "px",
                n = {
                    preload: "auto",
                    src: "http://vid-123636.hls.fastweb.broadcastapp.agoraio.cn/live/14926002743/index.m3u8",
                    "webkit-playsinline": !0,
                    playsinline: !0,
                    "x-webkit-airplay": !0,
                    "x5-video-player-type": "h5",
                    "x5-video-player-fullscreen": "true",
                    "x5-video-ignore-metadata": !0,
                    width: e.width,
                    height: e.height
                },
                o = [];
            e.isAutoPlay,
            e.isNeedPreload || delete n.preload;
            for (var a in n) o.push(a + "=" + n[a]);
            var s = "none";
            e.isNeedPoster && (s = "url(" + e.image + ")");
            var r = '<div class="inke-video-wrap" style="' + t + '"><video ' + o.join(" ") + ' ><p> 不支持video</p> </video><div class="i-v-mask"><div class="i-poster" style="background-image: ' + s + '"> </div> <span class="i-play-btn"></span><div class="i-loading"><div class="new-loding"><img src="//img2.inke.cn/MTQ4MjM3OTAwMTIwOCM2OTgjanBn.jpg"><div>请稍候...</div></div></div><div class="i-process-wrap"> <span class="i-process-bar"></span> <span class="i-process-dot"></span> <span class="i-process-time">00:00</span></div></div></div>';
            i.$container.append($(r)),
            i.video = i.$container.find("video")[0],
            i.$container.find("video").attr({
                    "x5-video-player-type": "h5",
                    "x5-video-player-fullscreen": "true"
                }),
            i.$wrap = i.$container.find(".inke-video-wrap"),
            i.$mask = i.$container.find(".i-v-mask"),
            i.$poster = i.$container.find(".i-poster")
        },
        play: function () {
            var i = this;
            try {
                i.video.play()
            } catch (e) {
                console.log("video play error ", JSON.stringfy(e))
            }
        },
        pause: function () {
            var i = this;
            i.video.pause()
        },
        getState: function () {
            var i = this;
            return i.state || ""
        },
        loadingTimer: null,
        showLoading: function (i) {
            var e = this,
                t = e.$wrap.find(".i-loading");
            i ? (t.css("display", "block"), e.loadingTimer = setTimeout(function () {
                    console.log("loading超时"),
                    e.showLoading(!1)
                }, 1e4)) : (clearTimeout(e.loadingTimer), e.loadingTimer = null, t.css("display", "none"))
        },
        processTimer: null,
        renderProcess: function () {
            function i() {
                var i = d.duration,
                    e = (t(i), d.currentTime / i);
                n(e),
                (e > .99 || d.currentTime >= d.duration) && (clearInterval(o.processTimer), o.processTimer = null)
            }
            function e(i) {
                clearInterval(o.processTimer);
                var e = i.pageX - s.position().left;
                if (!e) return void console.warn("touchSeek length is error");
                var t = e / s[0].offsetWidth;
                t < 0 && (t = 0),
                t > 1 && (t = 1),
                n(t),
                d.currentTime = t * d.duration
            }
            function n(i) {
                var e = t(d.duration),
                    n = i * s[0].offsetWidth - 2 + "px";
                r[0].style.width = n,
                l[0].style.left = n,
                c[0].innerHTML = t(d.currentTime) + " / " + e
            }
            var o = this,
                a = o.$wrap,
                s = a.find(".i-process-wrap"),
                r = a.find(".i-process-bar"),
                l = a.find(".i-process-dot"),
                c = a.find(".i-process-time"),
                d = o.video,
                u = 1e3;
            return !o.opt.isNeedProcessBar || 1 == o.opt.status || 1 == Page.gConfig.media_info.landscape && "game" == Page.gConfig.media_info.live_type ? (s.hide(), null) : (s.on("click", function (i) {}), l.on("touchstart", function (i) {
                    console.log("touchstart"),
                    o.processObj.stop(),
                    i.preventDefault(),
                    i.stopPropagation()
                }).on("touchmove", function (i) {
                    console.log("touchmove");
                    var t = i.touches[0];
                    e(t);
                    t.pageX;
                    i.preventDefault(),
                    i.stopPropagation()
                }).on("touchend", function (i) {
                    console.log("touchend"),
                    o.processObj.start(),
                    i.preventDefault(),
                    i.stopPropagation()
                }), {
                    start: function () {
                        clearInterval(o.processTimer),
                        o.processTimer = null,
                        o.processTimer = setInterval(i, u)
                    },
                    stop: function () {
                        clearInterval(o.processTimer),
                        o.processTimer = null
                    },
                    show: function (i) {
                        i ? s.css("display", "block") : s.css("display", "none")
                    }
                })
        },
        displayClickHandle: function () {
            var i = this,
                e = i.opt.events;
            if (i.isWaiting) return void console.log("isWaiting");
            if (i.video.paused) try {
                    i.video.play()
                } catch (t) {} else i.opt.isNeedPause && i.video.pause();
            o(e.onDisplayClick, t)
        },
        bindEvent: function () {
            var i = this,
                t = i.video,
                n = i.opt.events;
            t.addEventListener("play", function (t) {
                    e("event:play"),
                    i.state = "startPlay",
                    i.isStartPlay = !0,
                    i.$wrap.addClass("is-play"),
                    i.hasPlayed && i.showLoading(!0),
                    o(n.onPlay, t)
                }),
            t.addEventListener("pause", function (t) {
                    e("event:pause"),
                    i.state = "pausing",
                    i.$wrap.removeClass("is-play"),
                    i.processObj && (i.processObj.stop(), i.processObj.show(!1)),
                    i.$poster.removeClass("hide"),
                    o(n.onPause, t)
                }),
            t.addEventListener("error", function (t) {
                    e("event:error"),
                    i.state = "error",
                    "function" == typeof n.onError && n.onError()
                }),
            t.addEventListener("ended", function (t) {
                    e("event:ended"),
                    i.state = "ended",
                    i.processObj && (i.processObj.stop(), i.processObj.show(!1)),
                    o(n.onEnd, t)
                }),
            t.addEventListener("playing", function (t) {
                    console.log("playing time", (new Date).getTime()),
                    e("event:playing"),
                    i.state = "playing",
                    i.processObj && !i.processTimer && (i.processObj.stop(), i.processObj.start(), i.processObj.show(!0)),
                    i.isWaiting = !1,
                    i.showLoading(!1),
                    o(n.onPlaying, t)
                }),
            t.addEventListener("timeupdate", function (t) {
                    i.hasPlayed || (i.hasPlayed = !0),
                    i.$poster.hasClass("hide") || (e("poster_is_show"), i.$poster.addClass("hide"), "function" == typeof n.onPosterShow && n.onPosterShow(i.video)),
                    o(n.onTimeupdate, t)
                }),
            t.addEventListener("durationchange", function (e) {
                    i.hasPlayed || (i.hasPlayed = !0),
                    o(n.ondurationchange, e)
                }),
            t.addEventListener("progress", function (i) {}),
            t.addEventListener("waiting", function (t) {
                    e("event:waiting"),
                    i.state = "waiting",
                    i.processObj && i.processObj.stop(),
                    i.isWaiting = !0,
                    i.hasPlayed && i.showLoading(!0),
                    n.onWaiting || (n.onWaiting = n.onBuffer),
                    o(n.onWaiting, t)
                }),
            t.addEventListener("canplay", function (t) {
                    e("event:canplay"),
                    i.isCanplay = !0
                }),
            t.addEventListener("canplaythrough", function (i) {
                    e("event:canplaythrough")
                }),
            i.$mask.click(function (t) {
                    return e("mask_click"),
                    $(t.target).closest(".i-process-wrap").length > 0 ? void e("target is process") : i.isWaiting ? void console.log("isWaiting") : (i.video.paused ? i.video.play() : i.opt.isNeedPause && i.video.pause(), void o(n.onDisplayClick, t))
                }),
            $("video").click(function () {
                    console.log("click video")
                })
        }
    },
    i.InkePlayerMb = function (i, e) {
        return new n(i, e)
    },
    i.PlayerObj1 = n
}(window);
var PlayControl = {
    pageObj: null,
    player: null,
    mediaInfo: null,
    bufferStart: 0,
    logBufferState: "",
    logBufferTmpNum: 0,
    logTimer: null,
    conf: "",
    opt: {},
    isAndroid: /Android/i.test(navigator.userAgent),
    init: function (i, e) {
        var t = this;
        return t.pageObj = e || null,
        t.conf = i || {},
        t.bindEvent(),
        t
    },
    setUp: function (i, e) {
        var t = this;
        t.bufferStart = 0;
        var n = 640 * $(window).width() / 368,
            o = t.isAndroid ? n : "100%",
            a = {
                width: $(window).width(),
                height: o,
                file: "",
                controls: !1,
                autoStart: !0,
                image: "",
                status: 1,
                isNeedPause: !0,
                isNeedPoster: !0,
                isShowPoster: !0,
                isAutoPlay: !0,
                isNeedProcessBar: !0,
                events: {
                    onReady: t.onReady,
                    onPlay: t.onPlay,
                    onPause: t.onPause,
                    onPlaying: t.onPlaying,
                    onTimeupdate: t.onTimeupdate,
                    onWaiting: t.onWaiting,
                    onDisplayClick: t.onDisplayClick,
                    onSetupError: t.onSetupError,
                    onComplete: t.onComplete,
                    onIdle: t.onIdle,
                    onEnd: t.onEnd,
                    onError: t.onError
                }
            };
        $.extend(!0, a, i || {}),
        t.opt = a,
        t.opt.file || (t.opt.file = t.opt.playlist[0].file),
        t.player = InkePlayerMb("#container", t.opt),
        console.log("player defaults", t.opt),
        !t.conf.ua.isIOS || !t.conf.ua.isWeixin,
        t.logTimer && (clearInterval(t.logTimer), t.logTimer = null)
    },
    onReady: function () {
        console.log("onReady", (new Date).getTime())
    },
    startPlayTime: 1,
    onPlay: function () {
        console.log("onplay", (new Date).getTime());
        var i = PlayControl,
            e = i.conf.media_info;
        if (1 == i.startPlayTime && (i.startPlayTime = (new Date).getTime()), Common.log("player----onplay"), i.bufferStart) {
                var t = i.opt.file || i.opt.playlist && i.opt.playlist && i.opt.playlist[0].sources[0].file,
                    n = {
                        video_loadtime: (new Date).getTime() - i.bufferStart,
                        video_status: i.opt.status,
                        video_url: t || ""
                    };
                Common.trace({
                        report_type: "qa",
                        other: n
                    }),
                i.bufferStart = 0
            }
        $("#live-bg").hide(),
        $("video") && i.conf.ua.isAndroid && setTimeout(function () {
                $("video").height();
                $("#top").height(window.innerHeight);
                var i = parseInt(window.innerHeight - $("#top").height()) + 15;
                $(".btn-box").css("bottom", i),
                $("#topBom").css("bottom", i)
            }, 200),
        $("#js-top-id").show(),
        $("#js-looked-num").show(),
        $(".js-user-info-con").removeClass("up"),
        1 == e.status ? $(".btn-box").show() : ($(".btn-box").hide(), $("#hf-text").hide()),
        $("#topBom").show(),
        setTimeout(function () {
                $("#msg_box").show(),
                $("#js-gift-show-container").show()
            }, 50),
        $("#bestTop").hide()
    },
    onPlaying: function () {
        console.log("onPlaying", (new Date).getTime()),
        Common.log("player----onPlaying");
        var i = PlayControl,
            e = i.conf.media_info;
        Page.gConfig.ua.isAndroid && ($("#top2").addClass("android"), $("body").css("backgroundColor", "#000")),
        (1 == e.landscape && "game" == e.live_type || 1 == e.rotate) && (i.conf.ua.isIOS && ($("#container").addClass("screen-size"), $(".inke-video-wrap").css("height", "40%")), $(".inke-video-wrap video").css("object-fit", "contain"))
    },
    onTimeupdate: function () {
        var i = PlayControl;
        i.conf.media_info;
        if (Common.log("player----onTimeupdate"), i.startPlayTime && i.startPlayTime > 1) {
            try {
                var e = (new Date).getTime() - i.startPlayTime,
                    t = "other";
                i.conf.ua.isIOS ? t = "ios" : i.conf.ua.isAndroid && (t = "android"),
                _hmt.push(["_trackEvent", "share", "video", "load_time_" + t, e]),
                i.startPlayTime = 0
            } catch (n) {}
            i.startPlayTime = 0
        }
        if (i.bufferStart) {
            var o = i.opt.file || i.opt.playlist && i.opt.playlist && i.opt.playlist[0].sources[0].file,
                a = {
                    video_loadtime: (new Date).getTime() - i.bufferStart,
                    video_status: i.opt.status,
                    video_url: o || ""
                };
            Common.trace({
                    report_type: "qa",
                    other: a
                }),
            i.bufferStart = 0
        }
    },
    onPause: function () {
        console.log("onpause");
        var i = PlayControl;
        i.conf.media_info;
        if (i.logBufferTmpNum = 0, $("#live-bg").attr("class", "is-pause"), $(".user,#js-top-id").hide(), i.conf.ua.isAndroid) {
            var e = $("video") && $("video").height() || 0;
            e > i.conf.winHeight && setTimeout(function () {
                $("#top").height(window.innerHeight)
            }, 100)
        }
        $(".btn-box,#msg_box,#js-gift-show-container").hide(),
        $("#topBom").hide(),
        $("#bestTop").show(),
        Page.gConfig.ua.isAndroid && ($("#top2").removeClass("android"), $("body").css("backgroundColor", "#fff"))
    },
    onWaiting: function () {
        var i = PlayControl;
        console.log("onWaiting", (new Date).getTime()),
        i.bufferStart = (new Date).getTime(),
        i.logTimer || (i.logTimer = setInterval(function () {
            i.logBufferTimes()
        }, 1500))
    },
    onDisplayClick: function () {
        console.log("onDisplayClick", (new Date).getTime());
        var i = PlayControl,
            e = i.conf.media_info;
        i.pageObj.startPlay(),
        $(window).scrollTop(0),
        $("#live-bg").hide(),
        1 == e.status
    },
    onSetupError: function () {
        console.log("onSetupError", arguments)
    },
    onComplete: function () {
        var i = PlayControl,
            e = i.conf.media_info;
        window.console && console.log("onComplete"),
        1 == e.status && $(document).trigger("living:oncomplete")
    },
    onIdle: function () {
        console.log("onIdle", arguments)
    },
    onBeforeComplete: function () {
        console.log("onBeforeComplete", arguments)
    },
    onError: function () {
        console.error("player onError", arguments)
    },
    logBufferTimes: function () {
        var i = this,
            e = i.player.getState();
        if ("BUFFERING" == e) if (i.logBufferTmpNum > 0 && "playing" == i.logBufferState) {
                var t = i.opt.file || i.opt.playlist && i.opt.playlist && i.opt.playlist[0].sources[0].file;
                Common.trace({
                    report_type: "qa",
                    other: {
                        video_url: t || ""
                    }
                }),
                i.logBufferState = "buffer"
            } else i.logBufferTmpNum = i.logBufferTmpNum + 1;
        else "PLAYING" == e && (i.logBufferState = "playing")
    },
    bindEvent: function () {
        var i = this;
        $("#live-bg").on("click", function (e) {
            $(this).hasClass("is-finished") || i.onDisplayClick()
        }),
        $(".shadd3").click(function () {
            i.onDisplayClick(),
            $(".shadd3").hide()
        })
    }
},


    Page = {
        ua: {},
        isInit: !1,
        gConfig: "",
        queryData: "",
        playerObj: "",
        chatObj: "",
        giftObj: "",
        wrap: $("#js-all-wrap"),
        isLogin: !1,
        num_rand: Math.floor(5 * Math.random() + 0),
        init: function () {
            var i = this;
            i.initSize(),
            i.getUa(),
            i.getQuery(),
            i.getUserInfo().done(function () {});
            var e = (new Date).getTime();
            i.getConfig().done(function (t) {
                if (i.showLoading(!1), 1 * t.error_code === 0) {
                    var n = (new Date).getTime();
                    i.gConfig = $.extend(!0, i.gConfig || {}, t.data || {}),
                    i.gConfig.winWidth = i.wrap.width(),
                    i.gConfig.winHeight = $(window).height(),
                    i.playerObj = PlayControl.init(i.gConfig, i),
                    i.initStatus(),
                    i.initRedBag(),
                    t.data.view_uid && t.data.session && (i.isLogin = !0),
                    t.data.openid && Util.setCookie("openid4", t.data.openid),
                    i.setPageTitle(),
                    setTimeout(function () {
                        var e = 1;
                        1 != i.gConfig.isappinstalled && (e = 2),
                        i.gConfig.ua.isIOS || (e = 2),
                        i.userLog({
                            pop: e
                        })
                    }, 60),
                    setTimeout(function () {
                        i.initWeiXin()
                    }, 20),
                    _hmt.push(["_trackEvent", "share", "mobile_share_api", "time", n - e])
                }
            }).fail(function () {});
            var t = navigator.userAgent.match(/(iPhone\sOS|Android)\s(.*?)\s/),
                n = void 0,
                o = void 0;
            t && t[2] ? n = t[2].replace("_", ".").replace(";", "") : "",
            t && t[1] ? o = t[1] : "";
            var a = "other";
            i.gConfig.ua.isWeixin ? a = "weixin" : i.gConfig.ua.isWeibo ? a = "weibo" : i.gConfig.ua.isQQ && (a = "mqq"),
            _hmt.push(["_trackEvent", "share", o, o + n]),
            _hmt.push(["_trackEvent", "share", "browser", o + "_" + a]),
            setTimeout(function () {
                    HotAndRecordList.init(i.gConfig)
                }, 100),
            i.isInit || (i.isInit = !0, i.bindEvent())
        },
        initSize: function () {
            $("#top").height($(window).height())
        },
        setPageTitle: function () {
            var i = this,
                e = i.gConfig;
            e.wx && e.wx.share_desc
        },
        showOpenTip: function () {
            var i = this,
                e = $("#js-confirm-open-app"),
                t = $("#js-confirm-open-wrap");
            !i.gConfig.ua.isIOS,
            i.gConfig.isNeedOpenTip ? (e.show(), t.show()) : (t.hide(), e.hide()),
            e.on("click", ".js-ok-app-btn", function () {
                    i.userLog({
                        click_id: "open_app_dialog",
                        click_pos: 1
                    }),
                    i.goApp(!0),
                    setTimeout(function () {}, 500)
                }),
            e.on("click", ".js-cancel-app-btn", function () {
                    i.startPlay(),
                    setTimeout(function () {
                        t.hide(),
                        e.hide()
                    }, 200),
                    i.userLog({
                        click_id: "open_app_dialog",
                        click_pos: 2
                    })
                })
        },
        initStatus: function () {
            var i = this,
                e = i.gConfig.media_info;
            0 == e.status && !e.file.length || 1 == e.forbid || e.shieldstat === !1 ? i.renderNoLiveAndRecord() : (i.renderLiveOrRecord(), i.initPlay(), i.setOpenAppBtn()),
            $("#js-top-id").html(e.user.uid || ""),
            $("#js-follow-num").html(i.gConfig.fans || 0),
            i.updateUserNum(e.online_users),
            i.followBtn(),
            i.setDownUrl();
            var t = 1;
            0 == e.status && (t = e.file.length ? 3 : 2),
            _hmt.push(["_trackEvent", "share", "live_status", t])
        },
        getUa: function () {
            var i = this,
                e = Util.ua();
            i.ua = {
                    isiPad: e.ipad,
                    isiPhone: e.iphone,
                    isAndroid: e.android,
                    isWeixin: e.weixin,
                    isWeibo: e.weibo,
                    isQQ: e.mqq,
                    isIOS: e.ios
                },
            i.gConfig = $.extend(i.gConfig || {}, {
                    ua: i.ua
                })
        },
        getQuery: function () {
            var i = this;
            return i.queryData = Util.getQueryData() || {},
            i.queryData.liveid && i.queryData.uid ? (i.queryData.openid = Util.getCookie("openid4") || "", i.gConfig = $.extend(i.gConfig || {}, i.queryData), i.gConfig.open_time = parseInt((new Date).getTime()) || 0, i.gConfig.isNeedOpenTip = !1, i.gConfig.ua.isIOS && 1 == i.gConfig.isappinstalled && (i.gConfig.isNeedOpenTip = !0), void(i.gConfig.isNeedOpenTip = !1)) : (console.error("queryData_liveid_isnull"), !1)
        },
        getUserInfo: function () {
            var i = this;
            return i.queryData.liveid && i.queryData.uid ? Common.ajax({
                url: "/mobile/user_info",
                data: i.queryData,
                success: function (e) {
                    1 * e.error_code === 0 ? (i.gConfig = $.extend(i.gConfig || {}, e.data || {}), i.renderUserInfo()) : console.error(e.message)
                }
            }) : void alert("liveid uid is nul")
        },
        getConfig: function () {
            var i = this;
            return i.queryData.liveid && i.queryData.uid ? Common.ajax({
                url: "/mobile/mobile_share_api",
                data: i.queryData
            }) : void alert("liveid uid is nul")
        },
        renderUserInfo: function () {
            var i = this,
                e = (i.gConfig.media_info, i.gConfig.user);
            $("#live-bg").hide(),
            $(".user_nick").html(e.nick);
            var t = (new Date).getTime();
            $(".live-bg").on("load", function () {
                    i.logPageLoadTime();
                    var e = (new Date).getTime(),
                        n = e - t;
                    _hmt.push(["_trackEvent", "share", "poster", "time", n])
                });
            var n = Common.scaleImg({
                    url: e.pic,
                    w: 640,
                    h: 640
                });
            $(".user_pic,.live-bg").attr("src", n),
            $("#live-bg .big-bg").css("background-image", "url(" + n + ")"),
            $(".jibie").attr("src", "//img2.inke.cn/" + e.level_img),
            $("#js-user-bo-id").html(e.uid),
            0 == e.gender ? $(".gender").addClass("woman") : $(".gender").addClass("man"),
            i.gConfig.ua.isAndroid && $(".js-follow-btn").addClass("mid");
            var o = ["打开映客  立即勾搭主播", "打开映客客户端  看高清直播", e.nick + "邀请你陪TA聊天", "来不及解释了  快在映客上车", "更清晰，更流畅，上映客APP"],
                a = ["进入直播间", "进入直播间", "立即打开", "立即上车", "立即打开"],
                s = ["映客中打开  与主播更近一步", "在映客中打开  互动更精彩", "打开映客  与主播零距离互动", "主播邀请你来聊天", "打开映客  看高清直播"];
            $(".btm-text").html(o[i.num_rand]),
            $(".download-btn").html(a[i.num_rand]),
            $(".topBom").html(s[i.num_rand] + '<img src="//img2.inke.cn/MTQ4OTA1NjczOTM0NyMyNyNqcGc=.jpg">')
        },
        setTopClassName: function (i) {
            var e = $("#top"),
                t = ["is-finished", "is-live-playing", "is-live-pause", "is-record-playing", "is-record-pause"];
            return i === !1 ? void $.each(t, function (i, t) {
                    e.removeClass(t)
                }) : t.indexOf(i) == -1 ? void alert("class no exist") : ($.each(t, function (i, t) {
                    e.removeClass(t)
                }), void e.addClass(i))
        },
        renderNoLiveAndRecord: function () {
            var i = this;
            i.gConfig;
            $(".no-player-text").show(),
            $(".no-player-text").show(),
            $("#topBom").hide(),
            $("#hf-text").hide(),
            $("#live-bg").show().attr("class", "is-finished"),
            $("#top").height("16rem"),
            $("#bestTop").css("position", "fixed"),
            $("#top2").removeClass("top"),
            $("#shadow").show(),
            $("#js-gift-show-container").hide()
        },
        renderLiveOrRecord: function () {
            var i = this;
            i.gConfig.media_info;
            $("#shadow").hide()
        },
        renderRecord: function (i) {
            var e = this;
            e.gConfig.media_info;
            $(".no-player-text").hide(),
            e.updateUserNum(i.num || 0, 0)
        },
        initPlay: function () {
            var i = this,
                e = i.gConfig.media_info;
            if (e.status == -1) return void alert("此视频目前不能播放");
            if (1 == e.status) var t = {
                    file: e.file[0],
                    image: Common.scaleImg({
                        url: e.image,
                        w: 640,
                        h: 640
                    }),
                    skin: "http://apps.inke.tv/web/Public/jwplayer/jwplayer-skins-premium/vapor.xml"
                };
            else {
                    for (var n = [], o = 0; o < e.file.length; o++) n.push({
                        file: e.file[o],
                        image: e.image
                    });
                    var t = {
                        playlist: n,
                        image: Common.scaleImg({
                            url: e.image,
                            w: 640,
                            h: 640
                        }),
                        skin: "http://apps.inke.tv/web/Public/jwplayer/jwplayer-skins-premium/bekle.xml"
                    };
                    $("#shadow").click(function () {
                        $(this).hide(),
                        i.playerObj && i.playerObj.player && i.playerObj.player.play()
                    })
                }
            t.status = e.status,
            i.playerObj.setUp(t)
        },
        isAlreadyStart: !1,
        startPlay: function () {
            var i = this;
            i.isAlreadyStart || (i.playerObj && i.playerObj.player && i.playerObj.player.play(), i.userLog({
                click_id: "play_btn"
            }), i.initChatRoom(), i.isAlreadyStart = !0)
        },
        getUserNum: function () {
            var i = this,
                e = i.gConfig;
            0 != e.media_info.status && 1 != e.media_info.status || Common.ajax({
                    url: "/mobile/get_user_num",
                    data: {
                        liveid: e.liveid,
                        status: e.media_info.status
                    },
                    success: function (e) {
                        0 == e.error_code && e.data && i.updateUserNum(e.data.user_num || 0)
                    }
                })
        },
        updateUserNum: function (i, e) {
            var t = this,
                i = i || 0;
            $("#user_num").html(i + "人看过").show(),
            $("#user_num2").html(i);
            var n = $("#js-looked-num");
            return t.gConfig.ua.isAndroid && n.addClass("android"),
            void 0 !== e ? void n.removeClass("is-live").addClass("is-record") : void(1 == t.gConfig.media_info.status ? n.removeClass("is-record").addClass("is-live") : n.removeClass("is-live").addClass("is-record"))
        },
        setDownUrl: function () {
            var i = this,
                e = i.gConfig,
                t = i.gConfig.ua,
                n = Util.getQueryString("isappinstalled") || "",
                o = Util.getQueryString("share_from") || "",
                a = "http://www.ingkee.com",
                s = {
                    live: e.liveid,
                    user: e.uid,
                    pname: "room",
                    isappinstalled: n,
                    share_from: o
                },
                r = "//api.busi.inke.cn/open_app.html?" + $.param(s);
            $("#dakai,.js-red-link").attr("href", r),
            $("#js-redbag-con").attr("data-link", r),
            $(".topBom").attr("href", r),
            t.isIOS ? a = "https://itunes.apple.com/cn/app/id978985106" : t.isAndroid && (a = "http://a.app.qq.com/o/simple.jsp?pkgname=com.meelive.ingkee")
        },
        setOpenAppBtn: function () {
            var i = this,
                e = i.gConfig;
            e.liveid,
            i.gConfig.ua
        },
        followBtn: function () {
            function i() {
                n.addClass("disabled"),
                Common.ajax({
                    url: "/mobile/follow",
                    data: {
                        uid: t.uid,
                        view_uid: t.view_uid,
                        session: t.session
                    },
                    success: function (i) {
                        0 == i.error_code && (e.gConfig.is_follow = 1)
                    }
                }).always(function () {
                    n.removeClass("disabled")
                })
            }
            var e = this,
                t = e.gConfig,
                n = $(".js-follow-btn");
            !t.view_uid || !t.session,
            e.gConfig.is_follow && n.addClass("has").html("已关注"),
            n.on("click", function (t) {
                    var n = $(this);
                    n.hasClass("has") || n.hasClass("disabled") || (e.goApp(), n.html("已关注").addClass("has"), i(), e.userLog({
                        click_id: "focus"
                    }))
                })
        },
        initRedBag: function () {
            var i = this,
                e = i.gConfig,
                t = e.wx;
            if (e.uid && 1 * t.rp_money) {
                    var n = $("#js-redbag-main-tpl").html(),
                        o = $("#js-redbag-con");
                    o.html(n),
                    setTimeout(function () {
                            o.find(".js-view-nick").html(t.share_user_nick || ""),
                            o.find(".js-view-pic").attr("src", t.share_user_pic || ""),
                            o.find(".js-rp-money").html(t.rp_money || 0),
                            o.find(".js-red-link").attr("href", o.attr("data-link") || "//3g.inke.cn"),
                            o.show()
                        }, 0)
                }
        },

        initChatRoom: function () {
            var i = this,
                e = i.gConfig,
                t = e.liveid,
                n = e.view_uid || 0;
            t && e.sio.sio_ip ? (i.chatObj = new chat(i, {}), i.chatObj.enter_room(t, n)) : Util.log("initChatParamIsError"),
            i.chatBtnEvent()
        },
        chatBtnEvent: function () {
            var i = this;
            $("#js-talk-ipt").blur(function (i) {}),
            $("#js-start-talk").click(function (e) {
                return i.userLog({
                    click_id: "talk_start"
                }),
                i.goApp() ? void e.stopImmediatePropagation() : (window.scrollTo(0, 0), $("#msg_box").show(), $(".btn-box").hide(), $("#js-talk-ipt-wrap").show(), $("#js-talk-ipt").focus(), $(".shadd2").show(), void(i.gConfig.ua.isAndroid && setTimeout(function () {
                    var i = parseInt(window.innerHeight - $("#top").height()) + 10;
                    $("#js-talk-ipt-wrap").css("bottom", i)
                }, 50)))
            }),
            $("#gift_btn").on("click", function (e) {
                return i.userLog({
                    click_id: "gift_start"
                }),
                i.goApp() ? void e.stopImmediatePropagation() : void(i.gConfig.ua.isAndroid && setTimeout(function () {
                    var i = parseInt(window.innerHeight - $("#top").height()) + 10;
                    $(".gift-box").css("bottom", i)
                }, 100))
            }),
            $("#js-send-talk-btn").click(function () {
                var e = $("#js-talk-ipt").val();
                return "" == e ? void i.userLog({
                    click_id: "talk_send",
                    click_pos: 2
                }) : (i.userLog({
                    click_id: "talk_send",
                    click_pos: 1
                }), i.chatObj.send(e), $("#js-talk-ipt").val(""), void $("#js-talk-ipt").focus())
            }),
            $("#gift_send").on("click", function () {
                i.userLog({
                    click_id: "gift_send"
                })
            }),
            $("#js-goto-pay-btn").on("click", function () {
                i.userLog({
                    click_id: "gift_pay"
                })
            }),
            $("#js-talk-ipt").focus(function () {
                i.ua.isAndroid && setTimeout(function () {
                    window.scrollTo(0, 0)
                }, 100)
            }),
            $(".msg-box,#js-gift-show-container").on("click", function () {
                1 == i.gConfig.media_info.status && ($(".btn-box").show(), $("#js-talk-ipt-wrap").hide())
            })
        },
        controlBarHide: function () {
            setInterval(function () {
                $("#container_controlbar").css("display", "none")
            }, 50)
        },
        showLoading: function (i) {
            var e = $("#js-mask-loading");
            i ? e.show() : e.hide()
        },
        logPageLoadTime: function (i) {
            var e = this;
            if (i = i || (new Date).getTime(), !window.performance) return void console.log("不支持  performance");
            var t = window.IsNotRedirect || 1,
                n = 0;
            2 == window.IsNotRedirect && 1 * e.queryData.f_loadtime && (n = 1 * e.queryData.f_loadtime);
            var o = performance.timing;
            if (performance.now) var a = parseInt(performance.now());
            else var a = (o.domComplete || i) - o.navigationStart + n;
            var s = {
                    load_type: t,
                    imgloadtime: a,
                    allloadtime: (o.domComplete || i) - o.navigationStart + n,
                    api_end: 1 * i - o.navigationStart + n
                };
            Common.trace({
                    uid: e.gConfig.view_uid || "",
                    report_type: "qa",
                    other: s
                })
        },
        initWeiXin: function () {
            var i = this;
            i.gConfig.ua.isWeixin && i.gConfig.wx && Util.getScript("http://res.wx.qq.com/open/js/jweixin-1.0.0.js", function () {
                weixin_share(i.gConfig.wx)
            })
        },
        goApp: function (i, e) {
            var t = this,
                n = t.gConfig,
                o = t.gConfig.ua,
                a = !0,
                s = {
                    user: n.uid,
                    pname: "room",
                    isappinstalled: n.isappinstalled,
                    share_from: n.share_from
                },
                r = {
                    live: n.liveid,
                    user: n.uid,
                    pname: "room",
                    finalpage: "home"
                };
            1 == n.media_info.status ? s.live = n.liveid : (s.record = n.liveid, s.pname = "record");
            var l = "//api.busi.inke.cn/open_app.html?" + $.param(s),
                c = "http://a.app.qq.com/o/simple.jsp?pkgname=com.meelive.ingkee&android_schema=inke://" + $.param(r);
            if (o.isIOS && e && "more_live" == e.attr("data-id") && (l = "//api.busi.inke.cn/open_app.html?pname=hallhot&isappinstalled=" + (n.isappinstalled || 0)), i) {
                    var d = l;
                    return o.isAndroid && (d = c),
                    window.location.href = d,
                    a
                }
            return o.isIOS ? window.location.href = l : o.isAndroid && (t.isLogin ? a = !1 : window.location.href = c),
            a
        },
        userLog: function (i, e) {
            var t = this,
                n = t.gConfig,
                o = "",
                e = e || "click";
            n.ua.isIOS ? o = "ios" : n.ua.isAndroid && (o = "android");
            var a = 1;
            0 == n.media_info.status && (a = n.media_info.file.length ? 3 : 2);
            var s = {
                    share_time: n.share_time || "",
                    open_time: n.open_time || 0,
                    share_from: n.share_from || "",
                    share_uid: n.share_uid || "",
                    installed: n.isappinstalled || "",
                    uid: n.view_uid || "",
                    live_id: n.liveid || "",
                    live_uid: n.live_uid || "",
                    live_status: a || "",
                    app_type: o,
                    is_login: n.isLogin ? 1 : 0
                };
            $.extend(!0, s, i || {});
            var r = {
                    report_type: "wechat_share",
                    uid: n.view_uid || "",
                    other: s
                };
            Common.trace(r),
            i.click_id && "click" == e && _hmt.push(["_trackEvent", "share", "click_" + o, i.click_id])
        },
        bindEvent: function () {
            var i = this;
            $("#js-redbag-con").on("click", ".js-red-link", function (e) {
                return i.userLog({
                    click_id: "redbag"
                }),
                !0
            }),
            $("#js-redbag-con").on("click", ".red-close", function () {
                $("#js-redbag-con").hide()
            }),
            $("#live-bg").on("click", function (e) {
                i.chatObj ? setTimeout(function () {
                    i.chatObj.reStart()
                }, 100) : setTimeout(function () {
                    i.initChatRoom(),
                    $("#js-gift-show-container").show()
                }, 100),
                i.chatObj && i.chatObj.socket && i.chatObj.socket.socket.connected,
                i.userLog({
                    click_id: "play_btn"
                })
            }),
            $("#shadow").click(function () {
                i.playerObj || (console.log("提前play"), i.showLoading(!0))
            }),
            $(document).on("living:userNumUpdate", function (e, t) {
                i.updateUserNum(t.num)
            }),
            $(document).on("living:oncomplete", function (e, t) {
                i.renderNoLiveAndRecord()
            }),
            $(document).on("recordStartInit", function (e, t) {
                console.log(t),
                i.renderRecord(t),
                i.chatObj && i.chatObj.leaveRoom()
            }),
            $(window).resize(function () {
                setTimeout(function () {
                    window.scrollTo(0, 0)
                }, 100)
            }),
            $(".js-btn-open-app").on("click", function (e) {
                var t = $(this);
                t.attr("data-id") && (i.userLog({
                    click_id: t.attr("data-id")
                }, "open_click"), _hmt.push(["_trackEvent", "share", "click", t.attr("data-id"), Page.num_rand + 1])),
                i.goApp(!0, t),
                e.preventDefault()
            })
        }
    },
    HotAndRecordList = {
        $content: $(".tab-con-list"),
        config: null,
        isInit: !1,
        init: function (i) {
            var e = this;
            e.config = i,
            e.getHot(),
            e.isInit || (e.bindEvent(), e.isInit = !0)
        },
        getHot: function () {
            var i = this;
            Common.ajax({
                url: "/mobile/hot_list",
                data: {
                    uid: i.config.uid,
                    liveid: i.config.liveid
                },
                success: function (e) {
                    1 * e.error_code === 0 ? i.hotList(e) : alert(e.message)
                }
            })
        },
        hotList: function (i) {
            var e = this,
                t = i.data,
                n = [],
                o = $("#hot-list-tpl").html(),
                a = location.pathname.split("/");
            a.pop(),
            a.push("index.html");
            var s = a.join("/");
            s = location.pathname;
            for (var r = 0, l = t.length; r < l; r++) {
                    var c = t[r];
                    !c.name && (c.name = "你丑你先睡,我美我直播!" + c.nick + "正在直播,快来一起看~"),
                    !c.nick && (c.nick = "主播昵称");
                    var d = {
                        liveid: c.liveid,
                        uid: c.uid,
                        share_uid: c.uid,
                        share_from: e.config.share_from || "",
                        isappinstalled: e.config.isappinstalled || 0
                    };
                    c.url = s + "?" + $.param(d),
                    n.push(Util.parseTemplate(c, o))
                }
            $("#host-list").html(n.join("")),
            setTimeout(function () {
                    $(".icon-big").height($(".icon-big").width()),
                    $("#host-list").find(".l-top").height($(".icon-big").width()),
                    $("#host-list img.icon-big").picLazyLoad({
                        threshold: 200
                    })
                }, 25)
        },
        bindEvent: function () {
            $("#host-list").on("click", ".lists", function (i) {
                var e = $(this),
                    t = e.index();
                Page.userLog({
                        click_id: "host_list",
                        click_pos: t
                    }),
                window.location.href = e.attr("data-url")
            })
        }
    };
$(function () {
        Page.init()
    }),
window.onload = function (i) {
        if (!window.performance) return void console.log("不支持  performance");
        var e = performance.timing,
            t = (e.loadEventEnd - e.navigationStart, e.domComplete - e.navigationStart),
            n = e.domContentLoadedEventEnd - e.navigationStart,
            o = e.responseEnd - e.navigationStart;
        // _hmt.push(["_trackEvent", "share", "domComplete", "time", t]),
        // _hmt.push(["_trackEvent", "share", "domContentLoadedEventEnd", "time", n]),
        // _hmt.push(["_trackEvent", "share", "responseEnd", "time", o])
    };
