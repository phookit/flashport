$.fn.isOnScreen = function() {
    var element = this.get(0);
    var bounds = element.getBoundingClientRect();
    return bounds.top < window.innerHeight && bounds.bottom > 0;
}


var PhookitGallery = (function(options) {
    // private (settings)

    var defaults = {
        apiBase: 'http://127.0.0.1:8000/api',
        tagsIndex: '/tags/',
        imagesByTagRoot: '/images/t/',

        imageCountQueryParam: 'page_size',
        maxTagImageCount: 500,
        tagMenuListName: '.item-choice',
        tagMenuItemIdPrefix: '#menu-',
        
        imageMenuItemTemplate: '<div style="display: inline-block; opacity: 1;" class="col-lg-6 col-md-12 col-sm-12 col-xs-6 tag-{{tag_slug}}">'+
             '<div class="panel panel-default item">'+
                                '<div class="panel-heading">'+
                                    '<a href="{{url}}">'+
                                        '<img class="img-responsive item-img" src="{{thumbnail}}" alt="{{title}}">'+
                                    '</a>'+
                                '</div>'+
                                '<div class="panel-body">'+
                                    '<h4 class="item-title">{{title}}</h4>'+
                                    '<p class="item-description">{{description}}</p>'+
                                '</div>'+
                            '</div>'+
                        '</div>',

    };

    var options = $.extend({}, defaults, options); 

    var currentTag = 'latest';

    function _buildTagMenuItemName(slug) {
        return options.tagMenuItemIdPrefix + slug;
    }

    function _buildTagMenuId(slug) {
        return options.tagMenuListName + " " + _buildTagMenuItemName(slug);
    }

    function _addItemCount(url, item_count) {
        if( item_count ) {
            c = "?";
            if( url.indexOf("?") !== -1 ) {
                c = "&";
            }
            url = url + c + options.imageCountQueryParam + "=" + item_count;
        }
        return url;
    }


    function showLoading() {
        $("#target img").css('display', 'block');
        $("#target img").css('visibility', 'visible');
    }
    function hideLoading() {
        $("#target img").css('display', 'none');
        $("#target img").css('visibility', 'hidden');
    }

    function hideTags(tag_slug) {
        var items;
        if( tag_slug ) {
            console.log("hiding tag:"+tag_slug);
            items = $("#links .tag-"+tag_slug);
        }
        else {
            console.log("hiding all imgs");
            items = $("#links .tag");
        }
        items.each(function(index) {
            console.log("hiding idx:"+index);
            $(this).css('display', 'none');
            $(this).css('visibility', 'hidden');
        });
    }

    function showTags(tag_slug) {
        console.log("showing tags:"+tag_slug);
        var items = $("#links .tag-"+tag_slug);
        items.each(function(index) {
            $(this).css('display', 'inline-block');
            $(this).css('visibility', 'visible');
        });
    }


    function _addTagMenuItem(title, slug, prepend=false) {
        var item = $(_buildTagMenuId(slug))
        if(!item.length) {
            item = $("<a/>", {
                html: title,
                id: _buildTagMenuItemName(slug),
                href: "#"
            });
            //<a href="/gallery/{{t.slug}}" class="filter" id="menu-{{t.slug}}">{{t.title}}</a> 
            if( prepend ) {
                $(options.tagMenuListName).prepend(item);
            }
            else {
                $(options.tagMenuListName).append(item);
            }
        }
        item.attr("href", "#");
        item.click(
            {tag_slug: slug},
            function( event ) {
                console.log( "TAG:" + event.data.tag_slug + " clicked!");
                // TODO: Clear the image thumbnail list 
                tag = getTag(event.data.tag_slug);
                if( currentTag !== event.data.tag_slug ) {
                    //$("#links").html("");
                    hideTags(currentTag);

                    currentTag = event.data.tag_slug;

                    showTags(currentTag);
                    checkImageList();
                }
            }
        );
        return item;
    }

    function _addImageToUIList(tag, image_data) {
        var idx_offset = tag.imageCount() - image_data.length;
        console.log("OFFS:"+idx_offset+" IC:"+tag.imageCount() +" IDL:"+image_data.length);
        // new images have been added to an album, add them to the page
        for( var i in image_data ) {
            console.log("ADDING IMAGE:"+image_data[i].title);
            var s = options.imageMenuItemTemplate
                               .replace(/{{title}}/g, image_data[i].title);
            s = s.replace(/{{thumbnail}}/g,  image_data[i].thumbnail);
            s = s.replace(/{{description}}/g,  image_data[i].description);
            s = s.replace(/{{url}}/g,  image_data[i].url);
            s = s.replace(/{{tag_slug}}/g,  tag.slug);
            item = $("<div/>", {
                html: s,
            });
            console.log("GALL IDX:"+ (parseInt(i,10) + idx_offset));
            item.find("a").click(
                {tag_slug: tag.slug,
                 img_idx: (parseInt(i,10) + idx_offset),
                },
                function( event ) {
                    stopTimer();
                    event.preventDefault();
                    event.stopPropagation();
                    showGallery(event.data.tag_slug, event.data.img_idx);
                }
            );
            $("#links").append(item);
        }
    }

    function _buildImageURL(tag_slug) {
        return options.apiBase + options.imagesByTagRoot + tag_slug;
    }

    function _fetchImages(tag_slug) {
        console.log("fetchImages:" + tag_slug);
        var next_page = undefined;
        var tag = getTag( tag_slug );
        if( tag ) {
            next_page = tag.next_page;
            if( tag.imageCount() === 0 && !next_page ) {
                // load the first page of images for this album
                next_page = _buildImageURL(tag_slug);
            }
        }
        else {
            next_page = _buildImageURL('latest');
        }

        if( !next_page ) {
            return;
        }

        console.log("fetchImages ajax:" + next_page);
        return $.ajax(next_page, {
            dataType: 'json',
            success: function( resp ) {
                console.log("fetch images success");
                res = resp.results;
                tag.image_count = resp.count;
                tag.next_page = resp.next;
                tag.images.push.apply(tag.images, res);
            }
        });
    }

    var checkImageList = function(){
      console.log("checkImageList");  
      var tester = $('#target');
      var visible = tester.isOnScreen();
      if( visible ) {
            stopTimer();
            hideLoading();

            console.log("Target is visible: "+currentTag);
            $.when(_fetchImages(currentTag))
                .then(function(resp) {
                    var tag = getTag(currentTag);
                    console.log("resp="+resp);
                    if( resp ) {
                        _addImageToUIList(tag, resp.results);
                    }
                    if( tag.next_page ) {
                        startTimer();
                        showLoading();
                    }
                }
            );
      }
    }


    function showGallery(tag_slug, img_idx) {
        console.log("GAL INDEX:"+img_idx);
        var adaptImages = function(images) {
            var res = [];
            for( var i in images ) {
                res.push({
                    title: images[i].title,
                    href: images[i].public_filename,
                    type: 'image/jpeg',
                    thumbnail: images[i].thumbnail,
                });
            }
            return res;
        }

        var tag = getTag(tag_slug);
        var gall_images = adaptImages(tag.images);
          var gallery = blueimp.Gallery(
              gall_images,
              {
                  index: img_idx,
                  onslideend: function (index, slide) {

                      // TODO Add a delay here to stop scrolling too fast!!!

                      // Callback function executed after the slide change transition.
                      if( (index+1) === this.getNumber() ) {
                        $.when(_fetchImages(tag.slug))
                            .then(function(resp) {
                                console.log("slideend: resp="+resp);
                                if( resp ) {
                                    _addImageToUIList(tag, resp.results);
                                    gallery.add(adaptImages(resp.results));
                                }
                            });
                      }
                  },
                  onclose: function () {
                      checkImageList();
                  },
              }
            );

    }


    function showImage(filename, title, redirect) {
        image = {
            title: title,
            href: filename,
            type: 'image/jpeg',
        };

        var gallery = blueimp.Gallery(
            [ image ],
            {
                onclosed: function () {
                    // redirect to /
                    $(location).attr('href','/');
                },
            }
        );
    }


    // private objects
    function Tag(title, slug, is_super) { 
        this.title = title;
        this.slug = slug;
        this.is_super = is_super;
        this.next_page = undefined;
        this.image_count = 0;
        this.images = [];
        this.imageCount = function() {
            return this.images.length;
        }
    }

    var tags = {};

    var getTag = function(slug) {
        return tags[slug];
    }

    var addTag = function(data, cb) {
        console.log("adding tag:"+data.slug);
        t = new Tag(data.title, data.slug, data.main_tag);
        tags[data.slug] = t;
        cb(t)
    }

    var addTags = function(data, cb) {
        for (var r in data) {
            addTag(data[r], cb);
        }
    }

    function loadTags() {
        return $.ajax(options.apiBase + options.tagsIndex, {
            dataType: 'json',
            success: function( resp ) {
              // insert the "latest" option  
              addTag({title:"Latest",
                      slug:"latest",  
                      main_tag:"true",
              }, function(tag) {
                  _addTagMenuItem(tag.title, tag.slug);
              });

              addTags(resp, function(tag) {
                  _addTagMenuItem(tag.title, tag.slug);
              });
            }
        });
    }

    var timerHandle = undefined;

    function startTimer() {
        if( ! timerHandle ) {
            console.log("Starting timer");
            timerHandle = window.setInterval(checkImageList, 500);
        }
        else {
            console.log("Not starting timer, already running");
        }
    }
    function stopTimer() {
        if( timerHandle ) {
            console.log("stopping timer");
            window.clearInterval(timerHandle);
            timerHandle = undefined;
        }
        else {
            console.log("not stopping timer, not running");
        }
    }

    function onReady() {
        $.when(loadTags())
            .then(function(resp) {
            $("#links").html("");
            checkImageList();
            });
    }

    // Public API
    return {
        onReady: onReady,
        showImage: showImage,
    };
})();



