
create index activities_activitybase_priority on kukuicup.activities_activitybase (priority);
create index activities_activitybase_category_id on kukuicup.activities_activitybase (category_id);
create index activities_activitybase_category_priority on kukuicup.activities_activitybase (category_id, priority);

