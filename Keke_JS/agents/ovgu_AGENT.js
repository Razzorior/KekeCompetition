// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Milk 

//full_biy scores
//default 61%
//weird2.0 56.5%
//weird 55.4%
//dfs 48.9%

//phys_obj is_stopped = true, cannot pass through the object

//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation

let possActions = ["space", "right", "up", "left", "down"];

var an_action_set = [];

var counter  = 0;

var currentGamestate = simjs.getGamestate();
var isYouWin = [];

var WinIsSet = true;
var YouIsSet = true;

var playerObject = [];
var winObject = [];

var waitSequence = [];
var solveSequence = [];
var actions = [];
const wordFilter = ["stop", "sink", "push", "you", "kill", "hot", "move", "melt", "is", "you", "win"];

//saves the candidates for completion for every is-win combination with ascending manhattan distance
var candidatesWin = []

//saves the win candidates for completion for every something-is combination with ascending manhattan distance
var candidatesSomething = []

//saves the something-is combinations
var somethingIsCombinations = [];

//dump file rules for beginning of solution to check what we already have
//rules[] and rule_objs[]

//function which gives the position of all is-hot and is-melt objs

function informationHandler()
{
	//look for winnables
	if(currentGamestate.winnables.length >= 1)
	{
		winObject = currentGamestate.winnables[0];
		WinIsSet = true;
	}
	else
	{
		WinIsSet = false;
	}
	//look for players
	if(currentGamestate.players.length >= 1)
	{
		playerObject = currentGamestate.players[0];
		YouIsSet = true;
	}
	else
	{
		YouIsSet = false;
	}
}

function solution()
{
	//console.time('Execution Time');

	informationHandler();

	if(!WinIsSet || !YouIsSet)
	{
		isYouWin = isYouWinFilter();

		//look for auto movers
		waitSequence = resolveAutoMove();
		//interpreteRules(currentGamestate);
	}

	let playerX = playerObject.x;
	let playerY = playerObject.y;

	let winX = winObject.x;
	let winY = winObject.y;

	difX = winX - playerX;
	difY = winY - playerY;

	actions = pathToWin(difX,difY);

	an_action_set = an_action_set.concat(waitSequence,actions);

	//console.timeEnd('Execution Time');

	return an_action_set;
}

//returns positions of combinations isYou, isWin
//array[ isYou[], isWin[]]
function isConnectorsAnalysis(map)
{
	var temp = [];

	//analyses all is combinations
	for(const element of currentGamestate.is_connectors)
	{
		let entry = [];

		entry.push(object = 
			{name: map[element.y][element.x].name + map[element.y+1][element.x].name,
			y: map[element.y][element.x],
			x: map[element.y][element.x],
			dir: "up"});

		entry.push(object = 
			{name: map[element.y][element.x].name + map[element.y][element.x+1].name,
			y: map[element.y][element.x],
			x: map[element.y][element.x],
			dir: "left"});

		//other outcomes
		entry.push(object = 
			{name: map[element.y][element.x].name + map[element.y-1][element.x].name,
			y: map[element.y][element.x],
			x: map[element.y][element.x],
			dir: "down"});

		entry.push(object = 
			{name: map[element.y][element.x].name + map[element.y][element.x-1].name,
			y: map[element.y][element.x],
			x: map[element.y][element.x],
			dir: "right"});

		//saves the possible connection for the is tile
		temp.push(entry);
	}

	//positions of is-you combination
	let isYou = [];

	//position of is-win combination
	let isWin = [];

	//saves combinations into different arrays, coordinates refer to the middle block
	for(const element of temp)
	{
		let newName = [];
		if(element.name === "isyou")
		{
			isYou.push(data = {y: element.y, x: element.x});
		}
		if(element.name === "iswin")
		{
			isWin.push(data = {y: element.y, x: element.x});
		}
		if(!element.name.startsWith("is"))
		{
			somethingIsCombinations.push(data =
										{name: newName=element.name.replace("is",""),
										y: element.y,
										x: element.x,
										dir: element.dir});
		}
	}

	var output = [isYou,isWin];

	return output;
}

//add something to the Is-Win-Combo
function isWinCompletion(state)
{
	//filter possible meaningful rule completions 
	let possibleCompletions = filter(state.words, wordFilter);

	//checks if phys object exist for the possible rule to interact with
	let possiblePhys = filter(state.phys, wordFilter);

	//checks for combination of word and physics object
	let combinations = findCombinations(possibleCompletions, possiblePhys);

	//words where the adjacent fields are empty
	let candidates = checkNeighbors(combinations, currentGamestate.orig_map);


	//saves suitables words to the is-win combination and sorts by ascending manhattan distance
	for(const win of isYouWin[1])
	{
		let temp = [];

		for(const candidate of candidates)
		{
			let dist = manhattanDistance(win, candidate);
			temp.push(entry = {word: candidate.name, y: candidate.y, x: candidate.x, d: dist})
		}

		temp.sort(function(a,b){return a.d - b.d});
		candidatesWin.push(temp);
	}
}

//add win word to the Something-Is-Combo
function SomethingIsCompletion(somethingCombinations, state)
{
	//prunes all combinations which include a word from the filter list
	let candidates = filter(somethingCombinations,wordFilter);

	//checks if phys object exist for the possible rule to interact with
	let possiblePhys = filter(state.phys, wordFilter);

	//check if combination of word and phys exists
	somethingIsCombinations = findCombinations(candidates, possiblePhys);

	let winWords = filterWins(state.words);

	//calculates manhattan distances to win words
	for(const element of somethingIsCombinations)
	{
		let temp = [];

		for(const win of winWords)
		{
			let dist = manhattanDistance(element, win);
			temp.push(entry = {y: win.y, x: win.x, d: dist})
		}
		temp.sort(function(a,b){return a.d - b.d});
		candidatesSomething.push(temp);
	}
}

function resolveAutoMove()
{
	//automovers on the map
	var movers = currentGamestate.auto_movers;

	var pairsObjectiveMovers = [];

	if(movers.length < 1)
	{
		return [];
	}

	//search for combinations of automovers on the same height as isYou combinations
	for (const mover of movers)
	{
		for(const objective of isYouWin[0])
		{
			if(mover.y == objective[1])
			{
				//safe height plus x coordinates of the automover and is
				pairsObjectiveMovers.push([mover.y, mover.x, objective[0], mover.dir]);
			}
		}
	}

	var dist = 0;

	//looking for obj for completion on the the way
	for(const pair in pairsObjectiveMovers)
	{
		for(const obj in currentGamestate.obj_map[pair[0]])
		{	
			//obj hast to be between automover and is connector
			if(obj != undefined && obj.x < pair[1])
			{
				//distance is one lower because field is occupied
				dist = (pair[2] - pair[1])-1;

				//distance has to be reduced by because of pushable block
				if(pair[3] == "right")
				{
					dist -= 1;
				}
			}
		}
	}

	let output = [];

	for(let i = 0; i < dist; i += 1)
	{
		ouput.push("space");
	}
	
	/*
	if(counter < 1)
	{

	
	let print = JSON.stringify(currentGamestate.auto_movers);


	const fs = require('fs');
	fs.appendFile("../../autoMover", print, (err) => {
      
    // In case of a error throw err.
    if (err) throw err;
	});

	counter += 1;
	}
	*/

	return output;
}

//filter function which condense list by erasing entries
function filter(listToFilter, conditions)
{
	let temp = [];

	for(element in listToFilter)
	{
		if(conditions.includes(element.name))
		{}
		else
		{
			temp.push(element);
		}
	}

	return temp;
}

//return list of win objects with coordinates
function filterWins(mapWords)
{
	let temp = [];

	for(const element of mapWords)
	{
		if(element.name === "win")
		{
			temp.push(data = {y: element.y, x: element.x});
		}
	}

	return temp;
}

//finds combinations of words and phys object
function findCombinations(wordsInLevel, physInLevel)
{
	let temp = [];

	for(word in wordsInLevel)
	{
		for(phys in physInLevel)
		{
			if(phys.name === word.name)
			{
				temp.push(word);
			}
		}
	}

	return temp;
}

//returns array of hot and melt objects with position, includes player objects as well
function findHotMelt(state)
{
	let temp = [];

	//searches rules for is-melt and is-hot
	for(const element of state.rules)
	{
		if(element.includes("is-melt") || element.includes("is-hot"))
		{
			temp.push(element);
		}
	}

	let words = [];

	//trims the rules for the words only
	for(const element of temp)
	{
		let word1 = element.replace("-is-melt","");
		let word2 = word1.replace("-is-hot","");
		words.push(word2);
	}

	temp = [];

	//searches the objects corresponding to the words
	for(element of state.phys)
	{
		if(words.includes(element.name))
		{
			temp.push(element);
		}
	}

	return temp;
}

//check neighbors of a list of words, returns list of words where adjacent fields are empty
function checkNeighbors(candidates, map)
{
	let temp = [];

	for(word in candidates)
	{
		let checker = true;
		if(map[word.y][word.x+1] !== " "){ checker = false;}
		if(map[word.y-1][word.x] !== " "){ checker = false;}
		if(map[word.y][word.x-1] !== " "){ checker = false;}
		if(map[word.y+1][word.x] !== " "){ checker = false;}

		if(checker){ temp.push(word);}

		return temp;
	}
}

function somethingIsChecker(candidates, map)
{
	let temp = [];

	for(word in candidates)
	{
		let checker = true;
		if(map[word.y][word.x+1] !== " "){ checker = false;}
		if(map[word.y-1][word.x] == " "){ checker = false;}
		if(map[word.y][word.x-1] == " "){ checker = false;}
		if(map[word.y+1][word.x] !== " "){ checker = false;}

		if(checker){ temp.push(word);}

		return temp;
	}
}

//calculates manhatten distance between two points
function manhattanDistance(point1, point2)
{
	let difY = point1.y - point2.y;
	let difX = point1.x - point2.x;

	return Math.abs(difY) + Math.abs(difX);
}

//calculates action sequence for movement to specific x, y coordinates from current position
function pathToWin(x,y)
{
	let path = [];
	for(let i = 0; i < Math.abs(x); i +=1)
	{
		if(x < 0)
		{
			path.push("left");
		}
		else
		{
			path.push("right");
		}
	}
	
	for(let i = 0; i < Math.abs(y); i += 1)
	{
		if(y < 0)
		{
			path.push("up");
		}
		else
		{
			path.push("down");
		}
	}	

	return path;
}



// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state)
{
	// PERFORM ITERATIVE CALCULATIONS HERE //

	if(counter < 1)
	{
		let output = findHotMelt(init_state);
		//console.log(output);

	
	const fs = require('fs');
	fs.appendFile("../../debugHot", JSON.stringify(output), (err) => {
      
    // In case of a error throw err.
    if (err) throw err;
});

	counter += 1;
	}
	

	//return a sequence of actions or empty list
	return "sapce";
}



// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){},									// initializing function here
	best_sol : function(){return an_action_set;}
}