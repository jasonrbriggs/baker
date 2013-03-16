from baker import add_filter

def process(page):
    if 'shadow' in page.headers:
        print('got here %s' % page.headers['shadow'])

        for alt in page.headers['shadow'].split(','):
            page.content = ('''
<style type="text/css">
[alt="%s"] {
-moz-box-shadow: 4px 4px 5px #aaaaaa;
-webkit-box-shadow: 4px 4px 5px #aaaaaa;
box-shadow: 4px 4px 5px #aaaaaa;
/* For IE 8 */
-ms-filter: "progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#aaaaaa')";
/* For IE 5.5 - 7 */
filter: progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#aaaaaa');
}
</style>
''' % alt) + page.content

add_filter('pre-markdown', process)