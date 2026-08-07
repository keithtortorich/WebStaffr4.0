import sys
F = r"/Users/doc/Desktop/PROJECT DOC ws4 copy/sitesitesite.html"
with open(F, "r", encoding="utf-8") as f:
    s = f.read()

before = s.count("WebStaffr") + s.count("WebStaff")
s = s.replace("WebStaffr", "NetBuild.Pro")
s = s.replace("WebStaff", "NetBuild.Pro")
s = s.replace('<title>WebStaffr: Never Let a Paid Lead Go Unanswered</title>',
              '<title>NetBuild.Pro: Never Let a Paid Lead Go Unanswered</title>')
s = s.replace('content="WebStaffr gives contractors a trained virtual office team that answers calls, follows up with leads, and keeps the schedule full."',
              'content="NetBuild.Pro gives contractors a trained AI office team that answers calls, follows up with leads, and keeps the schedule full."')
s = s.replace('<meta name="theme-color" content="#000080">',
              '<meta name="theme-color" content="#1A1A2E">')
em = s.count("\u2014")
s = s.replace("\u2014", "-")

with open(F, "w", encoding="utf-8") as f:
    f.write(s)

print("brand replaced (WebStaffr+WebStaff):", before)
print("em-dashes replaced:", em)
print("remaining WebStaff:", s.count("WebStaff"), "remaining em-dash:", s.count("\u2014"))
print("title ok:", "NetBuild.Pro: Never Let a Paid Lead" in s)
print("theme ok:", 'content="#1A1A2E"' in s)
