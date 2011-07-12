// List of blocks on homepage. fallback should never be returned from server, it's shown only
// when JS is disabled or there are errors in AJAX request
var blocks = ['login', 'filelist', 'fileupload', 'fileinfo', 'sharebox', 'publish', 'filedelete',
    'flatpage', 'messages', 'fallback'];

/**
 * Directives to render blocks using PureJS
 * See docs: http://beebole.com/pure/documentation/
 */
var filelist_directives = {
    '.emptyMsg' : 'emptyMsg',
    '.files li' :  {
        'file <- files' :{
            'a' : 'file.file',
            'a@href' : 'file.link',
            'a@rel' : 'address:#{file.link}',
            'em' : 'file.uploaded_at',
            '.@class+' : function (arg) { return arg.item['public']?" public-file":""}
        }
    },
    '.pages option' : {
        'p <- pages' : {
            "@value" : 'p',
            "@selected" : function (arg) {return ((arg.pos+1) == arg.context.cur_page)?'selected' : ''},
            "." : 'p'
        }
    },
    '.pager@class' : function (arg) { return arg.context.pages.length > 1 ? '' : 'hidden'}
};
var fileupload_directives = {
    '.file-err' : 'errors.file',
    '.public-err' : 'errors.public',
    '.csrf_token@value' : 'csrf_token'
};
var fileinfo_directives = {
    'h3' : '#{file}#{errorMsg}',
    '.actions li' : {
        'action <- actions' : {
            'a' : 'action.action',
            'a@href' : 'action.url',
            'a@target' : function (arg) {return (arg.item.local)?'':'_blank'},
            'a@rel' : function(arg) {return (arg.item.local)?('address:'+arg.item.url):''}
        }
    },
    '.actions@class+' : function(arg) {return (typeof arg.context.actions == 'undefined')?' hidden':''},
    '.details .field' : {
        'field <- info' : {
            'strong' : 'field.name',
            'span' : 'field.value'
        }
    },
    '.details@class+' : function(arg) {return (typeof arg.context.info == 'undefined')?' hidden':''}
};
var sharebox_directives = {
    '.link@value' : 'absolute_link',
    'a.back@href' : 'link',
    'a.back@rel' : 'address:#{link}',
    '.share-form@action' : 'action',
    '.form-content' : 'form',
    'h3' : 'file'
};
var publish_directives = {
    'h3' : 'file',
    '.back@href' : 'back_link',
    '.back@rel' : 'address:#{back_link}',
    'form@action' : 'action_link',
    '.status' : 'status'
};
var filedelete_directives = {
    'h3' : 'file',
    '.back@href' : 'back_link',
    '.back@rel' : 'address:#{back_link}',
    'form@action' : 'action_link'
};
var messages_directives = {
    '.msg-display' : {
        'msg <- ' : {
            '.' : 'msg.message',
            '@class+' : " #{msg.tags}"
        }
    }
};
var instructions_directives = {
    'h3 .username' : function(attr) { return attr.context.username || 'Guest' },
    'p.auth@class' : function(attr) { return !attr.context.username && 'hidden' },
    'p.guest@class' : function(attr) { return !!attr.context.username && 'hidden' }
};
var flatpage_directives = {
    'h3' : 'title',
    '.content' : 'content'
};

function render_block(block, data) {
    /**
     * Helper for rendering blocks. Renders block with id='block' with data[block] using block_directives
     * On first run it compiles template to block_render function
     */
    if (typeof window[block+'_render'] == 'undefined') {
        window[block+'_render'] = $p("#"+block).compile(window[block+'_directives'])
    }
    $p("#"+block).render(data[block] || {}, window[block+'_render'])
}
function reload_callback(data) {
    /**
     * Check all blocks.
     * If block is present in data - make it visible and render with data[block]
     * else block is hidden
     *
     * instructions block is always shown
     */
    var block;
    var blockDiv;
    if (data.hasOwnProperty('redirect')) {
        if ($.address.value() != data.redirect)
            $.address.value(data.redirect)
        else
            $.address.update()
    }

    for (var i=0, blocksNum=blocks.length; i<blocksNum; i++ ) {
        block = blocks[i];
        if (data.hasOwnProperty(block)) {
            blockDiv = $("#"+block)
            blockDiv.show()
            render_block(block, data)
        }
        else {
            $("#"+block).hide()
        }
    }
    render_block('instructions', data)
}
function ajax_load(url) {
    /**
     * Load data via AJAX and pass results to reload_callback function
     * Redirects to home page on 404 error
     * */
    $.ajax({
        url : url,
        success : reload_callback,
        error : function(jqXHR, textStatus, errorThrown) {
            if (errorThrown == 'NOT FOUND')
                $.address.value('/')
        },
        dataType : 'json'
    })
}

/* JQuery-Django CSRF headers */
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && !settings.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});