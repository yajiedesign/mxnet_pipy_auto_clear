import requests
from lxml import etree

from get_want_del import project_list


def del_one_release(s, project, version):
    release_url = "https://pypi.org/manage/project/{0}/release/{1}/".format(project, version)
    release_first = s.get(release_url)
    if release_first.status_code != 200:
        print("get release error {0}/{1}".format(project, version))
        return
    release_first_html = etree.HTML(release_first.content)
    csrf_token = release_first_html.xpath('//*[@id="delete-release-modal"]/div/form/input')[0].attrib["value"]
    post_data = {"csrf_token": csrf_token, "confirm_version": version}
    rs = s.post(release_url, post_data, headers={'referer': release_url})
    if rs.status_code == 200:
        print("delete success {0}/{1}".format(project, version))
    else:
        print("delete fail {0}/{1}".format(project, version))


def del_one_project(s, project):
    with open("want_del/{0}.txt".format(project), "r", encoding="utf-8") as obj:
        for line in obj:
            sp = line.strip().split("\t")
            if sp[2] == "delete":
                del_one_release(s, project, sp[0])


def main():
    s = requests.session()
    login_url = 'https://pypi.org/account/login/'

    login_first = s.get(login_url)
    login_first_html = etree.HTML(login_first.content)
    csrf_token = login_first_html.xpath('//*[@id="content"]/section/div/form/input')[0].attrib["value"]

    with open("setting.txt", "r", encoding="utf-8") as obj:
        lines = obj.readlines()

    post_data = {"csrf_token": csrf_token, "username": lines[0].strip(),
                 "password": lines[1].strip()}
    rs = s.post(login_url, post_data, headers={'referer': login_url})
    if rs.status_code != 200:
        print("login error")
        return

    for project in project_list:
        del_one_project(s, project)

    pass


if __name__ == '__main__':
    main()
