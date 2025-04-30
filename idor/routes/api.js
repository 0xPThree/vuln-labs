const express = require("express");
const redis = require("redis");
const crypto = require("crypto");
const mysqlDB = require("../db.js");
const router = express.Router();
const client = redis.createClient({host: "redis-server", port: 6379});


const registerUser = (first_name, last_name, email, password, user_hash) => {
	// get the SHA1 sum of the password
	let passwordHash = crypto.createHash("sha1").update(password).digest("hex");

	// insert data to database
	let insertDataQuery = "INSERT INTO users (first_name, last_name, email, password, user_hash, phone_number, address, access_token, birth_place, posts_count, joined_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
	let values = [first_name, last_name, email, passwordHash, user_hash, "+0123456789", "21 jump street", "N07_SUP3R_S3CR37_4CC355_70K3N", "somewhere on earth", 0, "2025"];

	// insert data into database
	mysqlDB.query(insertDataQuery, values, (err, result) => {
		if (err) throw err
	});
}


router.post("/user", (req, res) => {
    const blacklistedFuzzers = ["python-requests", "Wfuzz", "Fuzz Faster"];

    // Check if auth cookie exists
    const authCookie = req.cookies.auth;
    if (!authCookie || authCookie.length !== 64) {
        return res.status(401).send("Invalid auth cookie");
    }

    // Check for fuzzing tools in user-agent
    if (blacklistedFuzzers.some(fuzzer => req.headers["user-agent"].startsWith(fuzzer))) {
        return res.status(403).send("bot detected");
    }

    // Get client's referer or IP address for rate limiting
    let requestRefererOrIP = req.headers.referer || req.connection.remoteAddress;
    client.incr(requestRefererOrIP);

    // Init requests counter
    client.get(requestRefererOrIP, (err, reply) => {
        let requestsCount = parseInt(reply);
        
        if (requestsCount === 1) {
            // Set expiry for referer/IP after 10 seconds
            client.expire(requestRefererOrIP, 10);
        }

        if (requestsCount > 365) {
            return res.status(429).send("Too many requests, wait for 10 seconds to make requests again");
        }

        // Extract user_hash and fetch user data
        let userHash = req.body.user_hash;

        // Query user data from database using user_hash
        let fetchUserDataQuery = "SELECT first_name, last_name, email, phone_number, access_token FROM users WHERE user_hash = ?";
        mysqlDB.query(fetchUserDataQuery, [userHash], (err, data) => {
            if (err) {
                return res.status(500).send("Database error");
            }
            if (data.length === 1) {
                // Don't send password in the response
                delete data[0].password;
                return res.json(data[0]);
            } else {
                return res.status(404).send("Invalid user hash");
            }
        });
    });
});

router.post("/register", (req, res) => {
	// extract post data
	let {first_name, last_name, email, password, user_hash} = req.body;

	// check if email is already registered
	let emailCheckQuery = "SELECT email FROM users WHERE email = ?";
	mysqlDB.query(emailCheckQuery, email, (err, row) => {
		if (err) throw err;
		if (row.length === 1) {
			res.status(409);
			res.send("email is already registered");
		} else {
			// register user
			registerUser(first_name, last_name, email, password, user_hash);

			// send 200 OK if everything went fine and redirect to login page
			res.status(200);
			res.send("registered successfully!");
		}
	});
});

router.post("/login", (req, res) => {
	// extract post data
	let {email, password} = req.body;

	// get the SHA1 sum of the password
	let passwordHash = crypto.createHash("sha1").update(password).digest("hex");

	// check if user exists
	let query = "SELECT email, password, user_hash FROM users WHERE email = ? AND password = ?";
	let values = [email, passwordHash];
	mysqlDB.query(query, values, (err, row) => {
		if (err) throw err;
		if (row.length > 0) {
			// create a dummy cookie and set it as auth cookie and redirect to homepage
			let authCookie = crypto.createHash("sha256").update(row[0]["password"] + row[0]["user_hash"]).digest("hex");
			res.cookie("auth", authCookie, {maxAge: 90000000})
			res.cookie("user_hash", row[0]["user_hash"], {maxAge: 90000000})
			res.status(302);
			res.redirect("/")
		} else {
			res.status(404);
			res.send("user does not exist");
		}
	});
});

module.exports = router;