const express = require("express");
const exphbs = require('express-handlebars');
const mysqlDB = require("./db.js");
const path = require("path");
const cookieParser = require('cookie-parser');
const app = express();
const apiRouter = require("./routes/api.js");
const port = 3000;

// handlebars options
app.engine('handlebars', exphbs({
    partialsDir: path.join(__dirname, 'views/partials') // Specify partials directory
}));
app.set('view engine', 'handlebars');

// Use cookie-parser middleware
app.use(cookieParser());

// make express handle json data and url encoded data
app.use(express.json());
app.use(express.urlencoded({extended: true}));

// tell express where to look for js and css files
app.use(express.static(path.join(__dirname, "assets")))

// route all API calls to the api-router (routes/api.js)
app.use("/api", apiRouter);

// check if auth cookie is set
const checkAuthCookie = (cookies) => {
    // check if auth cookie is set and valid
    return cookies && cookies.auth && cookies.auth.length === 64;
};

app.get('/', (req, res) => {
    if (!checkAuthCookie(req.cookies)) {
        return res.redirect("/login");
    }
    res.render("home", {
        title: "Home",
        bodyClass: "dark-body",
        includeNavbar: true,
        isActiveHome: true,
        isActiveProfile: false,
    });
});

app.get("/profile", (req, res) => {
    if (!checkAuthCookie(req.cookies)) {
        return res.redirect("/login");
    }
    res.render("profile", {
        title: "Profile",
        bodyClass: "dark-body",
        includeNavbar: true,
        isActiveHome: false,
        isActiveProfile: true,
    });
});

app.get("/login", (req, res) => {
    if (checkAuthCookie(req.cookies)) {
        return res.redirect("/");
    }

    res.render("login", {
        title: "Login",
        bodyClass: "dark-body d-flex justify-content-center align-items-center",
        includeNavbar: false
    });
});

app.get("/register", (req, res) => {
    if (checkAuthCookie(req.cookies)) {
        return res.redirect("/");
    }
    res.render("register", {
        title: "Register",
        bodyClass: "dark-body d-flex justify-content-center align-items-center",
        includeNavbar: false
    });
});

app.get("/logout", (req, res) => {
    res.cookie("auth", "", {expires: new Date(0)});
    res.cookie("user_hash", "", {expires: new Date(0)});
    res.redirect("/login");
});

// connect to MySQL
mysqlDB.connect(err => {
    if (err) throw err;
    console.log("MySQL connected...");
});

app.listen(port, () => {
    console.log(`app is running on port ${port}`)
});