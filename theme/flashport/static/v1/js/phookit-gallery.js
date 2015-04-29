"use strict";

$.fn.isOnScreen = function() {
    var element = this.get(0);
    var bounds = element.getBoundingClientRect();
    return bounds.top < window.innerHeight && bounds.bottom > 0;
};

var PhookitGallery = (function(optionsin) {
    // private (settings)

    var defaults = {
        apiBase: 'http://whathappensinvegas.co.uk/api',
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
                        '</div>'

    };

    var options = $.extend({}, defaults, optionsin); 

    var timerHandle = undefined;
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
            items = $("#links .tag-"+tag_slug);
        }
        else {
            items = $("#links .tag");
        }
        items.each(function(index) {
            $(this).css('display', 'none');
            $(this).css('visibility', 'hidden');
        });
    }

    function showTags(tag_slug) {
        var items = $("#links .tag-"+tag_slug);
        items.each(function(index) {
            $(this).css('display', 'inline-block');
            $(this).css('visibility', 'visible');
        });
    }


    function _addTagMenuItem(title, slug, prepend) {
        var item = $(_buildTagMenuId(slug));
        if(!item.length) {
            item = $("<a/>", {
                html: title,
                id: _buildTagMenuItemName(slug),
                href: "#"
            });
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
                // TODO: Clear the image thumbnail list 
                var tag = getTag(event.data.tag_slug);
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
        // new images have been added to an album, add them to the page
        for( var i in image_data ) {
            var s = options.imageMenuItemTemplate;

            s = s.replace(/{{title}}/g, image_data[i].title);
            s = s.replace(/{{thumbnail}}/g,  image_data[i].thumbnail);
            s = s.replace(/{{description}}/g,  image_data[i].description);
            s = s.replace(/{{url}}/g,  image_data[i].url);
            s = s.replace(/{{tag_slug}}/g,  tag.slug);

            var item = $("<div/>", {
                html: s
            });
            item.find("a").click(
                {tag_slug: tag.slug,
                 img_idx: (parseInt(i,10) + idx_offset)
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

        return $.ajax(next_page, {
            dataType: 'json',
            success: function( resp ) {
                var res = resp.results;
                tag.image_count = resp.count;
                tag.next_page = resp.next;
                tag.images.push.apply(tag.images, res);
            }
        });
    }

    var checkImageList = function(){
      var tester = $('#target');
      var visible = tester.isOnScreen();
      if( visible || !timerHandle) {
            stopTimer();
            hideLoading();

            $.when(_fetchImages(currentTag)).then(function(resp) {
                    var tag = getTag(currentTag);
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
    };


    function showGallery(tag_slug, img_idx) {
        var adaptImages = function(images) {
            var res = [];
            for( var i in images ) {
                res.push({
                    title: images[i].title,
                    href: images[i].public_filename,
                    type: 'image/jpeg',
                    thumbnail: images[i].thumbnail
                });
            }
            return res;
        };

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
                        $.when(_fetchImages(tag.slug)).then(function(resp) {
                                if( resp ) {
                                    _addImageToUIList(tag, resp.results);
                                    gallery.add(adaptImages(resp.results));
                                }
                            });
                      }
                  },
                  onclose: function () {
                      checkImageList();
                  }
              }
            );
    }


    function showImage(filename, title, redirect) {
        image = {
            title: title,
            href: filename,
            type: 'image/jpeg'
        };

        var gallery = blueimp.Gallery(
            [ image ],
            {
                onclosed: function () {
                    $(location).attr('href','/');
                }
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
        };
    }

    var tags = {};

    var getTag = function(slug) {
        return tags[slug];
    };

    var addTag = function(data, cb) {
        var t = new Tag(data.title, data.slug, data.main_tag);
        tags[data.slug] = t;
        cb(t);
    };

    var addTags = function(data, cb) {
        for (var r in data) {
            addTag(data[r], cb);
        }
    };

    function loadTags() {
        return $.ajax(options.apiBase + options.tagsIndex, {
            dataType: 'json',
            success: function( resp ) {
              // insert the "latest" option  
              addTag({title:"Latest",
                      slug:"latest",  
                      main_tag:"true"
              }, function(tag) {
                  _addTagMenuItem(tag.title, tag.slug, false);
              });

              addTags(resp, function(tag) {
                  _addTagMenuItem(tag.title, tag.slug, false);
              });
            }
        });
    }


    function startTimer() {
        if( ! timerHandle ) {
            timerHandle = window.setInterval(checkImageList, 500);
        }
    }
    function stopTimer() {
        if( timerHandle ) {
            window.clearInterval(timerHandle);
            timerHandle = undefined;
        }
    }

    function onReady() {
        $.when(loadTags()).then(function(resp) {
              $("#links").html("");
              checkImageList();
        });
    }

    // Public API
    return {
        onReady: onReady,
        showImage: showImage
    };
})();

