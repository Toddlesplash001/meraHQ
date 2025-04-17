const express = require("express");
const cors = require("cors");
const axios = require("axios");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json()); // Parse JSON requests

// Route to forward booking data to external API
app.post("/api/book", async (req, res) => {
  try {
    const payload = req.body;

    // Log received payload
    console.log("Received payload:", payload);

    const response = await axios.post(process.env.MYHQ_API_URL, payload, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    res.json(response.data); // Forward API response to frontend
  } catch (error) {
    console.error("API error:", error.response?.data || error.message);
    res
      .status(500)
      .json({ message: "API request failed", error: error.message });
  }
});

// Root route
app.get("/", (req, res) => {
  res.send("Backend is running");
});

app.get("/api/localities", async (req, res) => {
  try {
    const city = req.query.city;
    const lowerCity = city.toLowerCase();
    // https://api.web.myhq.in/workspace/web/filters/localities
    const payload = {
      selectedFilters: {
        CITY: lowerCity,
        PRODUCT: "MANAGED_OFFICE",
        LOCALITIES: [],
      },
    };
    console.log("request", payload);
    const response = await axios.post(
      process.env.MYHQ_LOCALITIES_URL,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    console.log(response);
    res.json(response.data);
  } catch (error) {
    console.error("API error:", error.response?.data || error.message);
    res
      .status(500)
      .json({ message: "API request failed", error: error.message });
  }
});
// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
