/**
 * MongoDB Aggregation & Query Examples
 * Purpose: Demonstrate NoSQL capabilities for semi-structured log analysis.
 * Author: Furkan Karakaya
 */

// ==========================================
// 1. Basic Aggregation: Event Counts by Type
// ==========================================
// Groups user events by type and sorts by popularity.
db.user_events.aggregate([
    {
        $group: {
            _id: "$event_type",
            count: { $sum: 1 }
        }
    },
    {
        $sort: { count: -1 }
    }
]);

// ==========================================
// 2. User User Session Analysis (Time Window)
// ==========================================
// Calculates the total time spent by each user on 'view_item' events.
// Assumes 'session_duration' field exists in metadata or root.
db.user_events.aggregate([
    {
        $match: {
            event_type: "view_item",
            "session_duration": { $exists: true, $ne: null }
        }
    },
    {
        $group: {
            _id: "$user_id",
            total_duration_seconds: { $sum: "$session_duration" },
            items_viewed: { $sum: 1 }
        }
    },
    {
        $project: {
            user_id: "$_id",
            total_duration_minutes: { $divide: ["$total_duration_seconds", 60] },
            items_viewed: 1,
            _id: 0
        }
    }
]);

// ==========================================
// 3. Product Popularity by Category
// ==========================================
// Finds the most interacted product categories.
db.user_events.aggregate([
    {
        $match: {
            category: { $exists: true }
        }
    },
    {
        $group: {
            _id: "$category",
            unique_users: { $addToSet: "$user_id" },
            total_interactions: { $sum: 1 }
        }
    },
    {
        $project: {
            category: "$_id",
            unique_user_count: { $size: "$unique_users" },
            total_interactions: 1,
            _id: 0
        }
    },
    {
        $sort: { total_interactions: -1 }
    }
]);

// ==========================================
// 4. Geospatial (Hypothetical)
// ==========================================
// If events had 'location' [lat, long], find events near a point.
/*
db.places.find({
   location: {
     $near: {
       $geometry: {
          type: "Point" ,
          coordinates: [ -73.9667, 40.78 ]
       },
       $maxDistance: 1000
     }
   }
})
*/
