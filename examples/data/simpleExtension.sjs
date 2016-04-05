function metadataFilter(context, params, content) {
	var mutableDoc = content.toObject();
	xdmp.log("context");
	xdmp.log(context);
	xdmp.log("params");
	xdmp.log(params);
	xdmp.log("content");
	xdmp.log(content);
	content = xdmp.unquote('<foo>hello</foo>', null, ["repair-none", "default-language=en"]);
	return content;
};

exports.transform = metadataFilter;