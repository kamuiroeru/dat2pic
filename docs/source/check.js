var nj = require('numjs');
var imshow = require("ndarray-imshow");
var d3 = require("d3");
var plotly = require('plotly')

const str2floats = (str, sep=/\s+/) => {
	var ret_array = [];
	var flag = true;
	for(var v of str.split(sep)){
		if (v) {
			var floated = parseFloat(v);
			if (!!Number.isNaN(floated)) {
				flag = false;
			}
			ret_array.push(parseFloat(v));
		}
	}
	return [flag, ret_array];
}

exports.s2f = str2floats

if (typeof require != 'undefined' && require.main==module) {
	console.log(str2floats('     123.2 -123  -234.32E+02'))
}

var form = document.forms.myform;
form.datfile.addEventListener('change', function(e) {
	var result = e.target.files[0];
	var reader = new FileReader();
	reader.readAsText(result);
	reader.addEventListener( 'load', function() {
		form.output.textContent = reader.result;
		var X = [], Y = [], U = [], V = [], T = [];
		for(var line of reader.result.split('\n')){
			if (line) {
				var [flag, d] = str2floats(line);
				if (flag){
					X.push(d[0]);
					Y.push(d[1]);
					U.push(d[2]);
					V.push(d[3]);
					T.push(d[4]);
				}
			}
		}
		var xsize = Array.from(new Set(X)).length;
		var ysize = Array.from(new Set(Y)).length;
		var xx = [], yy = [];
		for(var i=0; i < ysize; i++){
			xx.push(nj.arange(xsize));	
			yy.push(nj.zeros(xsize).add(i));	
		}
		var Xarr = nj.stack(xx).flatten().tolist()
		var Yarr = nj.stack(yy).flatten().tolist()
		console.log(Xarr);
		console.log(Yarr);
		var Uarr = nj.zeros([xsize, ysize])
		var Varr = nj.zeros([xsize, ysize])
		var Tarr = nj.zeros([xsize, ysize])
		// for (var i = 0;i < Xarr.length;i++){
		for (let i in Xarr){
			Uarr.set(Yarr[i], Xarr[i], U[i]);
			Varr.set(Yarr[i], Xarr[i], V[i]);
			Tarr.set(Yarr[i], Xarr[i], T[i]);
		}
		plot3(Uarr, Varr, Tarr, Xarr, Yarr)
		Uarr = Uarr.slice([null, null, -1], null)
		Varr = Varr.slice([null, null, -1], null)
		Tarr = Tarr.slice([null, null, -1], null)
		console.log(Uarr);
		console.log(Varr);
		console.log(Tarr);
		console.log(xsize);
		console.log(ysize);
		// plot2(Tarr.tolist())
	} )
})

const normarize = (njarray, omin=0, omax=1) => {
	let xmin = njarray.min(), xmax = njarray.max()
	return njarray.subtract(xmin).divide(xmax-xmin).multiply(omax-omin).add(omin)
}

const plot3 = (U, V, T, Xarr, Yarr) => {
	T = T.slice([1, -1], [1, -1])
	U = normarize(U, -1, 1)
	V = normarize(V, -1, 1)
	let U1 = U.slice([1, -1], [null, -2])
	let U2 = U.slice([1, -1], [1, -1])
	U = U1.add(U2).divide(2)
	let V1 = V.slice(2, [1, -1])
	let V2 = V.slice([1, -1], [1, -1])
	V = V1.add(V2).divide(2)
	let anotate_data = []
	let Uarr = U.tolist()
	let Varr = V.tolist()
	console.log(Uarr)
	console.log(Varr)
	for (let y in Uarr){
		for (let x in Uarr[y]){
			let d = {axref:"x", ayref: "y"}
			d["ax"] = parseInt(x)
			d["ay"] = parseInt(y)
			d["x"] = parseFloat(x) + parseFloat(Uarr[y][x])
			d["y"] = parseFloat(y) + parseFloat(Varr[y][x])
			d["showarrow"] = true
			d["arrowhead"] = 1
			d["arrowsize"] = 0.5
			d["arrowwidth"] = 5
			d["standoff"] = 2
			anotate_data.push(d)
			console.log(d)
		}
	}
	let data = [
		{
		z: T.tolist(),
		type: "heatmap",
		zmin: -0.5,
		zmax: 0.5,
		colorscale: 'Jet'
		}
	]
	let layout = {
		autosize: true,
		yaxis: {
			scaleanchor: "x"  // 1:1に固定
		},
		width: 1000,
		height: 1000,
		annotations: anotate_data
		
	}
	let graphOptions = {filename: "basic-heatmap", fileopt: "overwrite"}
	Plotly.newPlot("plotDiv" ,data, layout, graphOptions, (err, msg) => console.log(msg))
}

const plot = () => {
	var svg = d3.select("body").append("svg").attr("width", 500).attr("height", 100);
	var dataset = [1, 2, 3, 4, 5];
	var circles = svg.selectAll("circle")
		.data(dataset)
	    .enter()
	    .append("circle");
	circles.attr("cx", (d, lc) => lc * 50 + 25)
	.attr("cy", 50)
	.attr("r", (d) => 5*d)
	.attr("fill", "yellow")
	.attr("stroke", "orange")
	.attr("stroke-width", (d) => d)
}

// plot()


const plot2 = (matrix) => {
	// 1.データの準備
  var width = 1200; // グラフの幅
  var height = 800; // グラフの高さ
  var n = matrix.length
  // var matrix = new Array(n);
  // for(var i = 0; i < n; i++) {
  //   matrix[i] = new Array(n);
  //   for(var j = 0; j < n; j++) {
  //     matrix[i][j] = Math.random();
  //   }
  // }
 
  // 2. SVG領域の設定
  var svg = d3.select("body").append("svg").attr("width", width).attr("height", height);
  let g = svg.append("g").attr("transform", "translate(" + 0 + "," + 0 + ")");
 
  // 3. スケールの設定
  var scale = d3.scaleBand().rangeRound([0, d3.min([width, height])]).domain(d3.range(n));
 
  var color = d3.scaleSequential(
      function(t) { return d3.interpolate("white", "steelblue")(t); }
    )
    .domain([0, d3.max(matrix, function(row) { return d3.max(row) })]);
 
  // 4. ヒートマップの作成
	console.log(matrix)
	console.log(g)
  g.selectAll(".row")
    .data(matrix)
    .enter()
    .append("g")
    .attr("class", "row")
    .attr("transform", function(d, i) { return "translate(0," + scale(i) + ")"; })
    .selectAll(".cell")
    .data(function(d) { return d })
    .enter()
    .append("rect")
    .attr("class", "cell")
    .attr("x", function(d, i) { return scale(i); })
    .attr("width", scale.bandwidth())
    .attr("height", scale.bandwidth())
    .attr("opacity", 0.9)
    .attr("fill", function(d) { return color(d); });
}
