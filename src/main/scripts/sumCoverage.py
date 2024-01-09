import pickle
import os


def run(iter_dir):
    result = ""
    total_cov = []

    run_num = 0
    while True:
        csv_name = iter_dir+"/run-"+str(run_num).zfill(5)+"/results.pickle"
        if os.path.isfile(csv_name):
            with open(csv_name, "rb") as f:
                cov_str = pickle.load(f)
            if total_cov == []:
                for k in range(len(cov_str)):
                    total_cov.append(cov_str[k])
            else:
                for k in range(len(cov_str)):
                    if cov_str[k] == "1":
                        total_cov[k] = "1"

            total_count_cov = 0
            for i in total_cov:
                if i == "1":
                    total_count_cov += 1
            result += ("run-"+str(run_num).zfill(5) +
                       " : "+str(total_count_cov)+"\n")
            run_num += 1
        else:
            break
    return result

# if __name__ == "__main__":
#     iter_list = os.listdir(".")
#     for iter_dir in iter_list:
#         if os.path.isdir(iter_dir):
#             txt_name = iter_dir+"_cov.txt"
#             with open(txt_name, "w") as f:
#                 f.write(run(iter_dir))


if __name__ == "__main__":
    subjects = os.listdir("./results")
    for subject in subjects:
        if os.path.isdir("./results/" + subject):
            iter_dir = os.path.join("./results", subject, "Iteration-")
            iter_list = [iter_dir+"1", iter_dir+"2", iter_dir+"3", iter_dir+"4", iter_dir+"5"]
            if subject == "Rhino":
                mini_subject = "rhino"
            elif subject == "Argo":
                mini_subject = "argo"
            elif subject == "Genson":
                mini_subject = "genson"
            elif subject == "Gson":
                mini_subject = "gson"
            elif subject == "JsonToJava":
                mini_subject = "jsontojava"
            else:
                exit(0)
            iter_count = 1
            for iter_dir in iter_list:
                if os.path.isdir(iter_dir):
                    txt_name = "./results/"+mini_subject + \
                        "_cov_"+str(iter_count)+".txt"
                    print(txt_name)
                    with open(txt_name, "w") as f:
                        f.write(run(iter_dir))
                    iter_count += 1
